from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from AI_GO.core.child_flow.continuity_mutation.child_core_continuity_mutation import store
from .continuity_distribution_receipt_builder import (
    build_distribution_artifact,
    build_distribution_failure_receipt,
    build_distribution_hold_receipt,
    build_distribution_receipt,
)
from .continuity_distribution_registry import (
    get_profile_max_records,
    get_profile_shape_mode,
    is_allowed_policy_version,
    is_allowed_profile_scope,
    is_allowed_profile_target,
    is_allowed_profile_view,
    is_allowed_requesting_surface,
    is_allowed_scope,
    is_registered_profile,
    is_registered_target,
)
from .distribution_state import DistributionState, update_state


REQUIRED_REQUEST_KEYS = {
    "request_type",
    "request_id",
    "requesting_surface",
    "consumer_profile",
    "target_core",
    "continuity_scope",
    "read_reason",
    "requested_view",
    "policy_version",
    "timestamp",
}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _validate_request_structure(request: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(request, dict):
        return False, "invalid_input", "request must be a dictionary"

    if request.get("request_type") != "continuity_read_request":
        return False, "invalid_input", "invalid request type"

    missing = [key for key in sorted(REQUIRED_REQUEST_KEYS) if key not in request]
    if missing:
        return False, "structural_invalid", f"missing required request keys: {', '.join(missing)}"

    bad_keys = [key for key in sorted(REQUIRED_REQUEST_KEYS) if not _is_non_empty_string(request.get(key))]
    if bad_keys:
        return False, "structural_invalid", f"request keys must be non-empty strings: {', '.join(bad_keys)}"

    return True, None, "valid"


def _validate_registry(request: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    target = request["target_core"]
    scope = request["continuity_scope"]
    requester = request["requesting_surface"]
    view = request["requested_view"]
    policy_version = request["policy_version"]
    consumer_profile = request["consumer_profile"]

    if not is_registered_target(target):
        return False, "target_unlawful", "unknown target core"

    if not is_registered_profile(consumer_profile):
        return False, "consumer_profile_unlawful", "unknown consumer profile"

    if not is_allowed_requesting_surface(consumer_profile, requester):
        return False, "requester_unlawful", "requesting surface is not allowed for consumer profile"

    if not is_allowed_profile_target(consumer_profile, target):
        return False, "target_unlawful", "target core is not allowed for consumer profile"

    if not is_allowed_scope(target, scope):
        return False, "scope_unlawful", "invalid continuity scope for target"

    if not is_allowed_profile_scope(consumer_profile, scope):
        return False, "scope_unlawful", "continuity scope is not allowed for consumer profile"

    if not is_allowed_profile_view(consumer_profile, view):
        return False, "view_unlawful", "requested view is not allowed for consumer profile"

    if not is_allowed_policy_version(target, policy_version):
        return False, "policy_version_invalid", "distribution policy version is not allowed"

    return True, None, "valid"


def _get_target_records(target_core: str, continuity_scope: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for record in store.all().values():
        if (
            record.get("target_core") == target_core
            and record.get("continuity_scope") == continuity_scope
        ):
            records.append(record)

    records.sort(key=lambda item: item.get("source_timestamp", ""), reverse=True)
    return records


def _apply_view(records: List[Dict[str, Any]], requested_view: str, max_records: int) -> List[Dict[str, Any]]:
    if requested_view == "latest_record":
        return records[:1]

    if requested_view == "latest_n_records":
        return records[:max_records]

    if requested_view in {"refs_only", "summary_stub"}:
        return records[:max_records]

    return []


def _shape_by_profile(records: List[Dict[str, Any]], shape_mode: str) -> List[Dict[str, Any]]:
    if shape_mode == "refs_only":
        return [
            {
                "continuity_key": record.get("continuity_key"),
                "watcher_receipt_ref": record.get("watcher_receipt_ref"),
                "output_disposition_ref": record.get("output_disposition_ref"),
                "runtime_ref": record.get("runtime_ref"),
                "source_timestamp": record.get("source_timestamp"),
            }
            for record in records
        ]

    if shape_mode == "summary_stub":
        return [
            {
                "continuity_key": record.get("continuity_key"),
                "target_core": record.get("target_core"),
                "continuity_scope": record.get("continuity_scope"),
                "admission_basis": record.get("admission_basis"),
                "source_timestamp": record.get("source_timestamp"),
            }
            for record in records
        ]

    return [
        {
            "continuity_key": record.get("continuity_key"),
            "intake_id": record.get("intake_id"),
            "target_core": record.get("target_core"),
            "continuity_scope": record.get("continuity_scope"),
            "admission_basis": record.get("admission_basis"),
            "watcher_receipt_ref": record.get("watcher_receipt_ref"),
            "output_disposition_ref": record.get("output_disposition_ref"),
            "runtime_ref": record.get("runtime_ref"),
            "upstream_policy_version": record.get("upstream_policy_version"),
            "mutation_policy_version": record.get("mutation_policy_version"),
            "source_timestamp": record.get("source_timestamp"),
        }
        for record in records
    ]


def process_continuity_distribution(
    *,
    request: Dict[str, Any],
    state: Optional[DistributionState] = None,
) -> Dict[str, Any]:
    current_state = state or DistributionState()

    structure_ok, structure_code, structure_reason = _validate_request_structure(request)
    if not structure_ok:
        receipt = build_distribution_failure_receipt(
            request_id=request.get("request_id") if isinstance(request, dict) else None,
            target_core=request.get("target_core") if isinstance(request, dict) else None,
            requesting_surface=request.get("requesting_surface") if isinstance(request, dict) else None,
            consumer_profile=request.get("consumer_profile") if isinstance(request, dict) else None,
            rejection_code=structure_code or "invalid_input",
            reason=structure_reason,
            policy_version=request.get("policy_version") if isinstance(request, dict) else None,
        )
        update_state(
            current_state,
            request_id=receipt.get("request_id") or "unknown",
            target_core=receipt.get("target_core") or "unknown",
            requesting_surface=receipt.get("requesting_surface") or "unknown",
            consumer_profile=receipt.get("consumer_profile") or "unknown",
            disposition="rejected",
            receipt_type=receipt["receipt_type"],
            artifact_id=None,
            timestamp=receipt["timestamp"],
        )
        return {"status": "rejected", "receipt": receipt, "state": current_state.to_dict()}

    registry_ok, registry_code, registry_reason = _validate_registry(request)
    if not registry_ok:
        receipt = build_distribution_failure_receipt(
            request_id=request["request_id"],
            target_core=request["target_core"],
            requesting_surface=request["requesting_surface"],
            consumer_profile=request["consumer_profile"],
            rejection_code=registry_code or "target_unlawful",
            reason=registry_reason,
            policy_version=request["policy_version"],
        )
        update_state(
            current_state,
            request_id=request["request_id"],
            target_core=request["target_core"],
            requesting_surface=request["requesting_surface"],
            consumer_profile=request["consumer_profile"],
            disposition="rejected",
            receipt_type=receipt["receipt_type"],
            artifact_id=None,
            timestamp=receipt["timestamp"],
        )
        return {"status": "rejected", "receipt": receipt, "state": current_state.to_dict()}

    consumer_profile = request["consumer_profile"]
    max_records = get_profile_max_records(consumer_profile)
    shape_mode = get_profile_shape_mode(consumer_profile)

    records = _get_target_records(
        target_core=request["target_core"],
        continuity_scope=request["continuity_scope"],
    )

    view_limited_records = _apply_view(
        records=records,
        requested_view=request["requested_view"],
        max_records=max_records,
    )

    shaped_records = _shape_by_profile(
        records=view_limited_records,
        shape_mode=shape_mode,
    )

    artifact = build_distribution_artifact(
        target_core=request["target_core"],
        continuity_scope=request["continuity_scope"],
        requested_view=request["requested_view"],
        consumer_profile=consumer_profile,
        records=shaped_records,
    )

    receipt = build_distribution_receipt(
        request_id=request["request_id"],
        target_core=request["target_core"],
        requesting_surface=request["requesting_surface"],
        consumer_profile=consumer_profile,
        requested_view=request["requested_view"],
        artifact_id=artifact["distribution_id"],
        policy_version=request["policy_version"],
    )

    update_state(
        current_state,
        request_id=request["request_id"],
        target_core=request["target_core"],
        requesting_surface=request["requesting_surface"],
        consumer_profile=consumer_profile,
        disposition="fulfilled",
        receipt_type=receipt["receipt_type"],
        artifact_id=artifact["distribution_id"],
        timestamp=receipt["timestamp"],
    )

    return {
        "status": "fulfilled",
        "artifact": artifact,
        "receipt": receipt,
        "state": current_state.to_dict(),
    }
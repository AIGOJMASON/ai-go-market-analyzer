from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .consumption_state import ConsumptionState, update_state
from .continuity_consumption_receipt_builder import (
    build_consumption_failure_receipt,
    build_consumption_hold_receipt,
    build_consumption_receipt,
    build_strategy_packet,
)
from .continuity_consumption_registry import (
    CURRENT_CONSUMPTION_POLICY_VERSION,
    get_output_shape_mode,
    is_allowed_packet_class,
    is_allowed_requesting_surface,
    is_allowed_scope,
    is_allowed_target,
    is_allowed_transformation,
    is_allowed_upstream_distribution_policy_version,
    is_allowed_view,
    is_registered_profile,
)


REQUIRED_ARTIFACT_KEYS = {
    "artifact_type",
    "distribution_id",
    "target_core",
    "continuity_scope",
    "requested_view",
    "consumer_profile",
    "records",
    "record_count",
    "timestamp",
}

REQUIRED_RECEIPT_KEYS = {
    "receipt_type",
    "distribution_receipt_id",
    "request_id",
    "target_core",
    "requesting_surface",
    "consumer_profile",
    "requested_view",
    "artifact_id",
    "policy_version",
    "timestamp",
}


PROFILE_TO_TRANSFORMATION = {
    "pm_core_reader": "pm_planning_brief",
    "strategy_reader": "strategy_signal_packet",
    "child_core_reader": "child_core_context_packet",
}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _validate_artifact_structure(artifact: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(artifact, dict):
        return False, "invalid_input", "artifact must be a dictionary"

    if artifact.get("artifact_type") != "continuity_distribution_artifact":
        return False, "invalid_input", "invalid artifact type"

    missing = [key for key in sorted(REQUIRED_ARTIFACT_KEYS) if key not in artifact]
    if missing:
        return False, "structural_invalid", f"missing artifact keys: {', '.join(missing)}"

    string_keys = REQUIRED_ARTIFACT_KEYS - {"records", "record_count"}
    bad_keys = [key for key in sorted(string_keys) if not _is_non_empty_string(artifact.get(key))]
    if bad_keys:
        return False, "structural_invalid", f"artifact keys must be non-empty strings: {', '.join(bad_keys)}"

    if not isinstance(artifact.get("records"), list):
        return False, "structural_invalid", "artifact records must be a list"

    if not isinstance(artifact.get("record_count"), int):
        return False, "structural_invalid", "artifact record_count must be an integer"

    return True, None, "valid"


def _validate_receipt_structure(receipt: Any) -> Tuple[bool, Optional[str], str]:
    if not isinstance(receipt, dict):
        return False, "invalid_input", "receipt must be a dictionary"

    if receipt.get("receipt_type") != "continuity_distribution_receipt":
        return False, "invalid_input", "invalid receipt type"

    missing = [key for key in sorted(REQUIRED_RECEIPT_KEYS) if key not in receipt]
    if missing:
        return False, "structural_invalid", f"missing receipt keys: {', '.join(missing)}"

    bad_keys = [key for key in sorted(REQUIRED_RECEIPT_KEYS) if not _is_non_empty_string(receipt.get(key))]
    if bad_keys:
        return False, "structural_invalid", f"receipt keys must be non-empty strings: {', '.join(bad_keys)}"

    return True, None, "valid"


def _validate_alignment(artifact: Dict[str, Any], receipt: Dict[str, Any]) -> Tuple[bool, Optional[str], str]:
    if artifact["distribution_id"] != receipt["artifact_id"]:
        return False, "alignment_invalid", "distribution artifact id does not match receipt artifact_id"

    if artifact["target_core"] != receipt["target_core"]:
        return False, "alignment_invalid", "target_core mismatch between artifact and receipt"

    if artifact["consumer_profile"] != receipt["consumer_profile"]:
        return False, "alignment_invalid", "consumer_profile mismatch between artifact and receipt"

    if artifact["requested_view"] != receipt["requested_view"]:
        return False, "alignment_invalid", "requested_view mismatch between artifact and receipt"

    return True, None, "valid"


def _validate_registry(artifact: Dict[str, Any], receipt: Dict[str, Any], transformation_type: str) -> Tuple[bool, Optional[str], str]:
    profile = artifact["consumer_profile"]
    requesting_surface = receipt["requesting_surface"]
    target_core = artifact["target_core"]
    continuity_scope = artifact["continuity_scope"]
    requested_view = artifact["requested_view"]
    upstream_policy_version = receipt["policy_version"]

    if not is_registered_profile(profile):
        return False, "consumer_profile_unlawful", "unknown consumer profile"

    if not is_allowed_requesting_surface(profile, requesting_surface):
        return False, "requester_unlawful", "requesting surface is not allowed for consumer profile"

    if not is_allowed_target(profile, target_core):
        return False, "target_unlawful", "target core is not allowed for consumer profile"

    if not is_allowed_scope(profile, continuity_scope):
        return False, "scope_unlawful", "continuity scope is not allowed for consumer profile"

    if not is_allowed_view(profile, requested_view):
        return False, "view_unlawful", "requested view is not allowed for consumer profile"

    if not is_allowed_upstream_distribution_policy_version(upstream_policy_version):
        return False, "policy_version_invalid", "upstream distribution policy version is not allowed"

    if not is_allowed_transformation(profile, transformation_type):
        return False, "transformation_unlawful", "transformation type is not allowed for consumer profile"

    if not is_allowed_packet_class(profile, "continuity_strategy_packet"):
        return False, "packet_class_unlawful", "packet class is not allowed for consumer profile"

    return True, None, "valid"


def _shape_payload(
    *,
    profile: str,
    target_core: str,
    records: List[Dict[str, Any]],
    transformation_type: str,
) -> Dict[str, Any]:
    shape_mode = get_output_shape_mode(profile)

    if shape_mode == "pm_brief":
        return {
            "packet_class": "continuity_strategy_packet",
            "summary": {
                "target_core": target_core,
                "record_count": len(records),
                "latest_admission_basis": records[0].get("admission_basis") if records else None,
            },
            "lineage_refs": [
                {
                    "continuity_key": item.get("continuity_key"),
                    "watcher_receipt_ref": item.get("watcher_receipt_ref"),
                    "output_disposition_ref": item.get("output_disposition_ref"),
                    "runtime_ref": item.get("runtime_ref"),
                }
                for item in records[:5]
            ],
            "transformation_type": transformation_type,
        }

    if shape_mode == "strategy_signal":
        return {
            "packet_class": "continuity_strategy_packet",
            "signals": [
                {
                    "continuity_key": item.get("continuity_key"),
                    "admission_basis": item.get("admission_basis"),
                    "source_timestamp": item.get("source_timestamp"),
                }
                for item in records[:5]
            ],
            "target_core": target_core,
            "transformation_type": transformation_type,
        }

    return {
        "packet_class": "continuity_strategy_packet",
        "context_refs": [
            {
                "continuity_key": item.get("continuity_key"),
                "watcher_receipt_ref": item.get("watcher_receipt_ref"),
                "runtime_ref": item.get("runtime_ref"),
            }
            for item in records[:1]
        ],
        "target_core": target_core,
        "transformation_type": transformation_type,
    }


def process_continuity_consumption(
    *,
    artifact: Dict[str, Any],
    receipt: Dict[str, Any],
    state: Optional[ConsumptionState] = None,
) -> Dict[str, Any]:
    current_state = state or ConsumptionState()

    artifact_ok, artifact_code, artifact_reason = _validate_artifact_structure(artifact)
    if not artifact_ok:
        failure = build_consumption_failure_receipt(
            distribution_id=artifact.get("distribution_id") if isinstance(artifact, dict) else None,
            requesting_surface=receipt.get("requesting_surface") if isinstance(receipt, dict) else None,
            consumer_profile=artifact.get("consumer_profile") if isinstance(artifact, dict) else None,
            target_core=artifact.get("target_core") if isinstance(artifact, dict) else None,
            transformation_type=None,
            rejection_code=artifact_code or "invalid_input",
            reason=artifact_reason,
            upstream_policy_version=receipt.get("policy_version") if isinstance(receipt, dict) else None,
            consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
        )
        update_state(
            current_state,
            distribution_id=failure.get("distribution_id") or "unknown",
            requesting_surface=failure.get("requesting_surface") or "unknown",
            consumer_profile=failure.get("consumer_profile") or "unknown",
            target_core=failure.get("target_core") or "unknown",
            transformation_type="unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            packet_id=None,
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    receipt_ok, receipt_code, receipt_reason = _validate_receipt_structure(receipt)
    if not receipt_ok:
        failure = build_consumption_failure_receipt(
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt.get("requesting_surface") if isinstance(receipt, dict) else None,
            consumer_profile=artifact["consumer_profile"],
            target_core=artifact["target_core"],
            transformation_type=None,
            rejection_code=receipt_code or "invalid_input",
            reason=receipt_reason,
            upstream_policy_version=receipt.get("policy_version") if isinstance(receipt, dict) else None,
            consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
        )
        update_state(
            current_state,
            distribution_id=artifact["distribution_id"],
            requesting_surface=failure.get("requesting_surface") or "unknown",
            consumer_profile=artifact["consumer_profile"],
            target_core=artifact["target_core"],
            transformation_type="unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            packet_id=None,
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    alignment_ok, alignment_code, alignment_reason = _validate_alignment(artifact, receipt)
    if not alignment_ok:
        failure = build_consumption_failure_receipt(
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=artifact["consumer_profile"],
            target_core=artifact["target_core"],
            transformation_type=None,
            rejection_code=alignment_code or "alignment_invalid",
            reason=alignment_reason,
            upstream_policy_version=receipt["policy_version"],
            consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
        )
        update_state(
            current_state,
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=artifact["consumer_profile"],
            target_core=artifact["target_core"],
            transformation_type="unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            packet_id=None,
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    profile = artifact["consumer_profile"]
    transformation_type = PROFILE_TO_TRANSFORMATION.get(profile)
    if transformation_type is None:
        failure = build_consumption_failure_receipt(
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=profile,
            target_core=artifact["target_core"],
            transformation_type=None,
            rejection_code="transformation_unlawful",
            reason="no transformation type mapped for consumer profile",
            upstream_policy_version=receipt["policy_version"],
            consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
        )
        update_state(
            current_state,
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=profile,
            target_core=artifact["target_core"],
            transformation_type="unknown",
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            packet_id=None,
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    registry_ok, registry_code, registry_reason = _validate_registry(artifact, receipt, transformation_type)
    if not registry_ok:
        failure = build_consumption_failure_receipt(
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=profile,
            target_core=artifact["target_core"],
            transformation_type=transformation_type,
            rejection_code=registry_code or "consumer_profile_unlawful",
            reason=registry_reason,
            upstream_policy_version=receipt["policy_version"],
            consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
        )
        update_state(
            current_state,
            distribution_id=artifact["distribution_id"],
            requesting_surface=receipt["requesting_surface"],
            consumer_profile=profile,
            target_core=artifact["target_core"],
            transformation_type=transformation_type,
            disposition="rejected",
            receipt_type=failure["receipt_type"],
            packet_id=None,
            timestamp=failure["timestamp"],
        )
        return {"status": "rejected", "receipt": failure, "state": current_state.to_dict()}

    payload = _shape_payload(
        profile=profile,
        target_core=artifact["target_core"],
        records=artifact["records"],
        transformation_type=transformation_type,
    )

    packet = build_strategy_packet(
        target_core=artifact["target_core"],
        consumer_profile=profile,
        requesting_surface=receipt["requesting_surface"],
        continuity_scope=artifact["continuity_scope"],
        transformation_type=transformation_type,
        distribution_id=artifact["distribution_id"],
        source_request_id=receipt["request_id"],
        packet_payload=payload,
    )

    success = build_consumption_receipt(
        distribution_id=artifact["distribution_id"],
        requesting_surface=receipt["requesting_surface"],
        consumer_profile=profile,
        target_core=artifact["target_core"],
        transformation_type=transformation_type,
        packet_id=packet["packet_id"],
        upstream_policy_version=receipt["policy_version"],
        consumption_policy_version=CURRENT_CONSUMPTION_POLICY_VERSION,
    )

    update_state(
        current_state,
        distribution_id=artifact["distribution_id"],
        requesting_surface=receipt["requesting_surface"],
        consumer_profile=profile,
        target_core=artifact["target_core"],
        transformation_type=transformation_type,
        disposition="fulfilled",
        receipt_type=success["receipt_type"],
        packet_id=packet["packet_id"],
        timestamp=success["timestamp"],
    )

    return {
        "status": "fulfilled",
        "packet": packet,
        "receipt": success,
        "state": current_state.to_dict(),
    }
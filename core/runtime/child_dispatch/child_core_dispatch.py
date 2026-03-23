from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


FORBIDDEN_FIELDS = {
    "internal_state",
    "internal_notes",
    "private_notes",
    "debug",
    "debug_trace",
    "traceback",
    "_internal",
    "_debug",
    "_private",
}

DISPATCH_POLICY = {
    "proposal_saas": {
        "allowed_payload_classes": {"runtime_report_bundle"},
        "allowed_route_classes": {"internal_handoff"},
        "instruction_map": {
            "success": "generate_proposal",
            "retry_resolved": "generate_proposal",
            "escalated": "review_then_generate_proposal",
        },
    },
    "gis": {
        "allowed_payload_classes": {"runtime_report_bundle"},
        "allowed_route_classes": {"internal_handoff"},
        "instruction_map": {
            "success": "generate_mapping_action",
            "retry_resolved": "generate_mapping_action",
            "escalated": "review_then_generate_mapping_action",
        },
    },
    "wru": {
        "allowed_payload_classes": {"runtime_report_bundle"},
        "allowed_route_classes": {"internal_handoff"},
        "instruction_map": {
            "success": "generate_learning_asset",
            "retry_resolved": "generate_learning_asset",
            "escalated": "review_then_generate_learning_asset",
        },
    },
}


class ChildCoreDispatchError(ValueError):
    """Raised when Stage 54 child-core dispatch packet construction fails."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:10].upper()}"


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise ChildCoreDispatchError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ChildCoreDispatchError(f"{name} must be a dict")
    return value


def _require_field(payload: Dict[str, Any], field_name: str, artifact_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise ChildCoreDispatchError(f"{artifact_name}.payload.{field_name} is required")
    return value


def build_child_core_dispatch_packet(
    case_resolution: Dict[str, Any],
    target_child_core: str,
    dispatch_note: Optional[str] = None,
    issuing_authority: str = "RUNTIME_CHILD_CORE_DISPATCH",
) -> Dict[str, Any]:
    """
    Stage 54 — bounded dispatch preparation only.

    Consumes one approved case_resolution and emits one
    child_core_dispatch_packet for one approved child core.
    """
    _assert_no_internal_field_leakage(case_resolution, "case_resolution")
    case_resolution = _require_dict("case_resolution", deepcopy(case_resolution))

    artifact_type = case_resolution.get("artifact_type")
    if artifact_type != "case_resolution":
        raise ChildCoreDispatchError(
            f"case_resolution.artifact_type must be 'case_resolution', got {artifact_type!r}"
        )

    payload = case_resolution.get("payload")
    if not isinstance(payload, dict):
        raise ChildCoreDispatchError("case_resolution.payload must be a dict")

    case_resolution_id = _require_field(payload, "case_resolution_id", "case_resolution")
    case_id = _require_field(payload, "case_id", "case_resolution")
    final_state = _require_field(payload, "final_state", "case_resolution")
    source_path = _require_field(payload, "source_path", "case_resolution")
    payload_class = _require_field(payload, "payload_class", "case_resolution")
    route_class = _require_field(payload, "route_class", "case_resolution")
    execution_mode = _require_field(payload, "execution_mode", "case_resolution")
    actionable = payload.get("actionable")
    sealed = payload.get("sealed")
    instruction = payload.get("instruction")

    if sealed is not True:
        raise ChildCoreDispatchError("case_resolution.payload.sealed must be True")

    if actionable is not True:
        raise ChildCoreDispatchError("case_resolution.payload.actionable must be True")

    if instruction != "downstream_dispatch_permitted":
        raise ChildCoreDispatchError(
            "case_resolution.payload.instruction must be 'downstream_dispatch_permitted'"
        )

    if final_state not in {"success", "retry_resolved", "escalated"}:
        raise ChildCoreDispatchError(
            "case_resolution.payload.final_state must be one of success, retry_resolved, or escalated"
        )

    if target_child_core not in DISPATCH_POLICY:
        raise ChildCoreDispatchError(f"target_child_core is not approved: {target_child_core!r}")

    policy = DISPATCH_POLICY[target_child_core]

    if payload_class not in policy["allowed_payload_classes"]:
        raise ChildCoreDispatchError(
            f"payload_class {payload_class!r} is not allowed for target_child_core {target_child_core!r}"
        )

    if route_class not in policy["allowed_route_classes"]:
        raise ChildCoreDispatchError(
            f"route_class {route_class!r} is not allowed for target_child_core {target_child_core!r}"
        )

    target_instruction = policy["instruction_map"].get(final_state)
    if not target_instruction:
        raise ChildCoreDispatchError(
            f"no dispatch instruction configured for final_state {final_state!r} "
            f"and target_child_core {target_child_core!r}"
        )

    dispatch_packet_id = _make_id("WR-CHILD-DISPATCH")
    created_at = _utc_timestamp()

    return {
        "artifact_type": "child_core_dispatch_packet",
        "payload": {
            "dispatch_packet_id": dispatch_packet_id,
            "case_id": case_id,
            "case_resolution_id": case_resolution_id,
            "created_at": created_at,
            "issuing_authority": issuing_authority,
            "target_child_core": target_child_core,
            "dispatch_ready": True,
            "instruction": target_instruction,
            "final_state": final_state,
            "source_path": source_path,
            "payload_class": payload_class,
            "route_class": route_class,
            "execution_mode": execution_mode,
            "resolution_confidence": payload.get("resolution_confidence"),
            "authoritative_receipt_id": payload.get("authoritative_receipt_id"),
            "observed_branches": deepcopy(payload.get("observed_branches", [])),
            "dispatch_note": dispatch_note,
            "sealed": True,
        },
    }
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

APPROVED_CHILD_CORES = {
    "proposal_saas",
    "gis",
    "wru",
}

APPROVED_INTAKE_DECISIONS = {
    "accepted",
    "rejected",
}


class ChildCoreIntakeReceiptError(ValueError):
    """Raised when Stage 55 child-core intake receipt construction fails."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:10].upper()}"


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise ChildCoreIntakeReceiptError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ChildCoreIntakeReceiptError(f"{name} must be a dict")
    return value


def _require_field(payload: Dict[str, Any], field_name: str, artifact_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise ChildCoreIntakeReceiptError(f"{artifact_name}.payload.{field_name} is required")
    return value


def build_child_core_intake_receipt(
    child_core_dispatch_packet: Dict[str, Any],
    intake_decision: str,
    intake_reason: Optional[str] = None,
    accepted_by: Optional[str] = None,
    issuing_authority: str = "RUNTIME_CHILD_CORE_INTAKE",
) -> Dict[str, Any]:
    """
    Stage 55 — child-core intake acknowledgement only.

    Consumes one approved child_core_dispatch_packet and emits one
    child_core_intake_receipt confirming lawful boundary acceptance or rejection.
    """
    _assert_no_internal_field_leakage(child_core_dispatch_packet, "child_core_dispatch_packet")
    child_core_dispatch_packet = _require_dict(
        "child_core_dispatch_packet",
        deepcopy(child_core_dispatch_packet),
    )

    artifact_type = child_core_dispatch_packet.get("artifact_type")
    if artifact_type != "child_core_dispatch_packet":
        raise ChildCoreIntakeReceiptError(
            "child_core_dispatch_packet.artifact_type must be "
            f"'child_core_dispatch_packet', got {artifact_type!r}"
        )

    payload = child_core_dispatch_packet.get("payload")
    if not isinstance(payload, dict):
        raise ChildCoreIntakeReceiptError("child_core_dispatch_packet.payload must be a dict")

    dispatch_packet_id = _require_field(payload, "dispatch_packet_id", "child_core_dispatch_packet")
    case_id = _require_field(payload, "case_id", "child_core_dispatch_packet")
    case_resolution_id = _require_field(payload, "case_resolution_id", "child_core_dispatch_packet")
    target_child_core = _require_field(payload, "target_child_core", "child_core_dispatch_packet")
    dispatch_ready = payload.get("dispatch_ready")
    sealed = payload.get("sealed")
    instruction = _require_field(payload, "instruction", "child_core_dispatch_packet")

    if sealed is not True:
        raise ChildCoreIntakeReceiptError("child_core_dispatch_packet.payload.sealed must be True")

    if dispatch_ready is not True:
        raise ChildCoreIntakeReceiptError(
            "child_core_dispatch_packet.payload.dispatch_ready must be True"
        )

    if target_child_core not in APPROVED_CHILD_CORES:
        raise ChildCoreIntakeReceiptError(
            f"child_core_dispatch_packet.payload.target_child_core is not approved: "
            f"{target_child_core!r}"
        )

    if intake_decision not in APPROVED_INTAKE_DECISIONS:
        raise ChildCoreIntakeReceiptError(
            f"intake_decision must be one of {sorted(APPROVED_INTAKE_DECISIONS)}"
        )

    if intake_decision == "rejected" and not intake_reason:
        raise ChildCoreIntakeReceiptError("intake_reason is required when intake_decision='rejected'")

    if intake_decision == "accepted":
        intake_status = "child_core_intake_accepted"
        actionable_downstream = True
    else:
        intake_status = "child_core_intake_rejected"
        actionable_downstream = False

    intake_receipt_id = _make_id("WR-CHILD-INTAKE")
    created_at = _utc_timestamp()

    return {
        "artifact_type": "child_core_intake_receipt",
        "payload": {
            "intake_receipt_id": intake_receipt_id,
            "case_id": case_id,
            "case_resolution_id": case_resolution_id,
            "dispatch_packet_id": dispatch_packet_id,
            "created_at": created_at,
            "issuing_authority": issuing_authority,
            "target_child_core": target_child_core,
            "intake_decision": intake_decision,
            "intake_status": intake_status,
            "accepted_by": accepted_by,
            "intake_reason": intake_reason,
            "instruction": instruction,
            "final_state": payload.get("final_state"),
            "source_path": payload.get("source_path"),
            "payload_class": payload.get("payload_class"),
            "route_class": payload.get("route_class"),
            "execution_mode": payload.get("execution_mode"),
            "resolution_confidence": payload.get("resolution_confidence"),
            "authoritative_receipt_id": payload.get("authoritative_receipt_id"),
            "observed_branches": deepcopy(payload.get("observed_branches", [])),
            "actionable_downstream": actionable_downstream,
            "sealed": True,
        },
    }
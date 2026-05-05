from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict
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


class CaseCloseoutRecordError(ValueError):
    """Raised when Stage 56 case closeout construction fails."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:10].upper()}"


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise CaseCloseoutRecordError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise CaseCloseoutRecordError(f"{name} must be a dict")
    return value


def _require_field(payload: Dict[str, Any], field_name: str, artifact_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise CaseCloseoutRecordError(f"{artifact_name}.payload.{field_name} is required")
    return value


def build_case_closeout_record(
    case_resolution: Dict[str, Any],
    child_core_dispatch_packet: Dict[str, Any],
    child_core_intake_receipt: Dict[str, Any],
    issuing_authority: str = "RUNTIME_CASE_CLOSEOUT",
) -> Dict[str, Any]:
    """
    Stage 56 — final lifecycle archival closeout only.

    Consumes one approved case_resolution, one approved
    child_core_dispatch_packet, and one approved child_core_intake_receipt,
    then emits one case_closeout_record.
    """
    _assert_no_internal_field_leakage(case_resolution, "case_resolution")
    _assert_no_internal_field_leakage(child_core_dispatch_packet, "child_core_dispatch_packet")
    _assert_no_internal_field_leakage(child_core_intake_receipt, "child_core_intake_receipt")

    case_resolution = _require_dict("case_resolution", deepcopy(case_resolution))
    child_core_dispatch_packet = _require_dict(
        "child_core_dispatch_packet",
        deepcopy(child_core_dispatch_packet),
    )
    child_core_intake_receipt = _require_dict(
        "child_core_intake_receipt",
        deepcopy(child_core_intake_receipt),
    )

    if case_resolution.get("artifact_type") != "case_resolution":
        raise CaseCloseoutRecordError(
            "case_resolution.artifact_type must be 'case_resolution'"
        )
    if child_core_dispatch_packet.get("artifact_type") != "child_core_dispatch_packet":
        raise CaseCloseoutRecordError(
            "child_core_dispatch_packet.artifact_type must be 'child_core_dispatch_packet'"
        )
    if child_core_intake_receipt.get("artifact_type") != "child_core_intake_receipt":
        raise CaseCloseoutRecordError(
            "child_core_intake_receipt.artifact_type must be 'child_core_intake_receipt'"
        )

    resolution_payload = case_resolution.get("payload")
    dispatch_payload = child_core_dispatch_packet.get("payload")
    intake_payload = child_core_intake_receipt.get("payload")

    if not isinstance(resolution_payload, dict):
        raise CaseCloseoutRecordError("case_resolution.payload must be a dict")
    if not isinstance(dispatch_payload, dict):
        raise CaseCloseoutRecordError("child_core_dispatch_packet.payload must be a dict")
    if not isinstance(intake_payload, dict):
        raise CaseCloseoutRecordError("child_core_intake_receipt.payload must be a dict")

    case_resolution_id = _require_field(resolution_payload, "case_resolution_id", "case_resolution")
    resolution_case_id = _require_field(resolution_payload, "case_id", "case_resolution")
    resolution_final_state = _require_field(resolution_payload, "final_state", "case_resolution")
    resolution_source_path = _require_field(resolution_payload, "source_path", "case_resolution")
    resolution_sealed = resolution_payload.get("sealed")

    dispatch_packet_id = _require_field(
        dispatch_payload,
        "dispatch_packet_id",
        "child_core_dispatch_packet",
    )
    dispatch_case_id = _require_field(dispatch_payload, "case_id", "child_core_dispatch_packet")
    dispatch_case_resolution_id = _require_field(
        dispatch_payload,
        "case_resolution_id",
        "child_core_dispatch_packet",
    )
    dispatch_target_child_core = _require_field(
        dispatch_payload,
        "target_child_core",
        "child_core_dispatch_packet",
    )
    dispatch_instruction = _require_field(
        dispatch_payload,
        "instruction",
        "child_core_dispatch_packet",
    )
    dispatch_sealed = dispatch_payload.get("sealed")
    dispatch_ready = dispatch_payload.get("dispatch_ready")

    intake_receipt_id = _require_field(
        intake_payload,
        "intake_receipt_id",
        "child_core_intake_receipt",
    )
    intake_case_id = _require_field(intake_payload, "case_id", "child_core_intake_receipt")
    intake_case_resolution_id = _require_field(
        intake_payload,
        "case_resolution_id",
        "child_core_intake_receipt",
    )
    intake_dispatch_packet_id = _require_field(
        intake_payload,
        "dispatch_packet_id",
        "child_core_intake_receipt",
    )
    intake_target_child_core = _require_field(
        intake_payload,
        "target_child_core",
        "child_core_intake_receipt",
    )
    intake_decision = _require_field(
        intake_payload,
        "intake_decision",
        "child_core_intake_receipt",
    )
    intake_status = _require_field(
        intake_payload,
        "intake_status",
        "child_core_intake_receipt",
    )
    intake_sealed = intake_payload.get("sealed")

    if resolution_sealed is not True:
        raise CaseCloseoutRecordError("case_resolution.payload.sealed must be True")
    if dispatch_sealed is not True:
        raise CaseCloseoutRecordError("child_core_dispatch_packet.payload.sealed must be True")
    if intake_sealed is not True:
        raise CaseCloseoutRecordError("child_core_intake_receipt.payload.sealed must be True")
    if dispatch_ready is not True:
        raise CaseCloseoutRecordError("child_core_dispatch_packet.payload.dispatch_ready must be True")

    case_ids = {resolution_case_id, dispatch_case_id, intake_case_id}
    if len(case_ids) != 1:
        raise CaseCloseoutRecordError("all artifacts must share the same case_id")

    if dispatch_case_resolution_id != case_resolution_id:
        raise CaseCloseoutRecordError(
            "child_core_dispatch_packet.payload.case_resolution_id must match case_resolution"
        )
    if intake_case_resolution_id != case_resolution_id:
        raise CaseCloseoutRecordError(
            "child_core_intake_receipt.payload.case_resolution_id must match case_resolution"
        )
    if intake_dispatch_packet_id != dispatch_packet_id:
        raise CaseCloseoutRecordError(
            "child_core_intake_receipt.payload.dispatch_packet_id must match child_core_dispatch_packet"
        )
    if intake_target_child_core != dispatch_target_child_core:
        raise CaseCloseoutRecordError(
            "child_core_intake_receipt.payload.target_child_core must match dispatch target"
        )

    if intake_decision == "accepted":
        closeout_state = "closed_accepted"
    elif intake_decision == "rejected":
        closeout_state = "closed_rejected"
    else:
        raise CaseCloseoutRecordError("intake_decision must be 'accepted' or 'rejected'")

    closeout_record_id = _make_id("WR-CASE-CLOSEOUT")
    created_at = _utc_timestamp()

    return {
        "artifact_type": "case_closeout_record",
        "payload": {
            "closeout_record_id": closeout_record_id,
            "case_id": resolution_case_id,
            "case_resolution_id": case_resolution_id,
            "dispatch_packet_id": dispatch_packet_id,
            "intake_receipt_id": intake_receipt_id,
            "created_at": created_at,
            "issuing_authority": issuing_authority,
            "closeout_state": closeout_state,
            "final_state": resolution_final_state,
            "source_path": resolution_source_path,
            "target_child_core": dispatch_target_child_core,
            "dispatch_instruction": dispatch_instruction,
            "intake_decision": intake_decision,
            "intake_status": intake_status,
            "payload_class": resolution_payload.get("payload_class"),
            "route_class": resolution_payload.get("route_class"),
            "execution_mode": resolution_payload.get("execution_mode"),
            "resolution_confidence": resolution_payload.get("resolution_confidence"),
            "authoritative_receipt_id": resolution_payload.get("authoritative_receipt_id"),
            "observed_branches": deepcopy(resolution_payload.get("observed_branches", [])),
            "sealed": True,
        },
    }
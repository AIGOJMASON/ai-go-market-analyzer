from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List
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

ALLOWED_BRANCHES = {"primary", "retry", "escalation"}
SUCCESS_STATUSES = {
    "delivered",
    "success",
    "succeeded",
    "completed",
    "retry_succeeded",
    "retry_resolved",
    "escalation_completed",
    "escalation_succeeded",
    "escalated",
}
FAILURE_STATUSES = {
    "delivery_failed",
    "failed",
    "retry_failed",
    "escalation_failed",
    "terminal",
    "terminal_failure",
}


class CaseResolutionError(ValueError):
    """Raised when Stage 53 case resolution construction fails."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:10].upper()}"


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise CaseResolutionError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise CaseResolutionError(f"{name} must be a dict")
    return value


def _require_list(name: str, value: Any) -> List[Any]:
    if not isinstance(value, list):
        raise CaseResolutionError(f"{name} must be a list")
    return value


def _require_field(payload: Dict[str, Any], field_name: str, artifact_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise CaseResolutionError(f"{artifact_name}.payload.{field_name} is required")
    return value


def _normalize_replay_entry(entry: Dict[str, Any], index: int) -> Dict[str, Any]:
    entry_name = f"replay_chain[{index}]"
    entry = _require_dict(entry_name, deepcopy(entry))

    sequence = _require_field(entry, "sequence", entry_name)
    if sequence != index + 1:
        raise CaseResolutionError(f"{entry_name}.sequence must equal {index + 1}")

    branch_class = _require_field(entry, "branch_class", entry_name)
    if branch_class not in ALLOWED_BRANCHES:
        raise CaseResolutionError(f"{entry_name}.branch_class must be one of {sorted(ALLOWED_BRANCHES)}")

    artifact_type = _require_field(entry, "artifact_type", entry_name)
    receipt_id = _require_field(entry, "receipt_id", entry_name)
    occurred_at = _require_field(entry, "occurred_at", entry_name)
    outcome_status = _require_field(entry, "outcome_status", entry_name)
    route_class = _require_field(entry, "route_class", entry_name)
    payload_class = _require_field(entry, "payload_class", entry_name)
    execution_mode = _require_field(entry, "execution_mode", entry_name)

    return {
        "sequence": sequence,
        "branch_class": branch_class,
        "artifact_type": artifact_type,
        "receipt_id": receipt_id,
        "occurred_at": occurred_at,
        "outcome_status": outcome_status,
        "route_class": route_class,
        "payload_class": payload_class,
        "execution_mode": execution_mode,
        "result_ref": entry.get("result_ref"),
        "source_receipt_ref": entry.get("source_receipt_ref"),
    }


def _derive_final_state(last_entry: Dict[str, Any]) -> str:
    branch = last_entry["branch_class"]
    status = str(last_entry["outcome_status"]).strip().lower()

    if branch == "primary" and status in SUCCESS_STATUSES:
        return "success"
    if branch == "retry" and status in SUCCESS_STATUSES:
        return "retry_resolved"
    if branch == "escalation" and status in SUCCESS_STATUSES:
        return "escalated"
    if status in FAILURE_STATUSES:
        return "terminal_failure"

    raise CaseResolutionError(
        f"unable to derive final_state from branch={branch!r} outcome_status={last_entry['outcome_status']!r}"
    )


def build_case_resolution(
    audit_replay_index: Dict[str, Any],
    issuing_authority: str = "RUNTIME_CASE_RESOLUTION",
) -> Dict[str, Any]:
    """
    Stage 53 — final-state collapse only.

    Consumes one approved audit_replay_index and emits one exclusive
    case_resolution artifact.
    """
    _assert_no_internal_field_leakage(audit_replay_index, "audit_replay_index")
    audit_replay_index = _require_dict("audit_replay_index", deepcopy(audit_replay_index))

    artifact_type = audit_replay_index.get("artifact_type")
    if artifact_type != "audit_replay_index":
        raise CaseResolutionError(
            f"audit_replay_index.artifact_type must be 'audit_replay_index', got {artifact_type!r}"
        )

    payload = audit_replay_index.get("payload")
    if not isinstance(payload, dict):
        raise CaseResolutionError("audit_replay_index.payload must be a dict")

    audit_replay_index_id = _require_field(payload, "audit_replay_index_id", "audit_replay_index")
    case_id = _require_field(payload, "case_id", "audit_replay_index")
    replay_chain_raw = _require_field(payload, "replay_chain", "audit_replay_index")
    replay_chain_raw = _require_list("audit_replay_index.payload.replay_chain", replay_chain_raw)

    if not replay_chain_raw:
        raise CaseResolutionError("audit_replay_index.payload.replay_chain must not be empty")

    trace_complete = payload.get("trace_complete")
    sealed = payload.get("sealed")
    resolution_pending = payload.get("resolution_pending")

    if trace_complete is not True:
        raise CaseResolutionError("audit_replay_index.payload.trace_complete must be True")
    if sealed is not True:
        raise CaseResolutionError("audit_replay_index.payload.sealed must be True")
    if resolution_pending is not True:
        raise CaseResolutionError("audit_replay_index.payload.resolution_pending must be True")

    normalized_chain = [
        _normalize_replay_entry(entry, index) for index, entry in enumerate(replay_chain_raw)
    ]

    if normalized_chain[0]["branch_class"] != "primary":
        raise CaseResolutionError("replay_chain must begin with the primary branch")

    branch_order = [entry["branch_class"] for entry in normalized_chain]
    if len(branch_order) != len(set(branch_order)):
        raise CaseResolutionError("replay_chain may contain only one entry per branch_class")

    legal_prefixes = [
        ["primary"],
        ["primary", "retry"],
        ["primary", "retry", "escalation"],
    ]
    if branch_order not in legal_prefixes:
        raise CaseResolutionError("replay_chain branch order is invalid")

    route_classes = {entry["route_class"] for entry in normalized_chain}
    payload_classes = {entry["payload_class"] for entry in normalized_chain}
    execution_modes = {entry["execution_mode"] for entry in normalized_chain}

    last_entry = normalized_chain[-1]
    final_state = _derive_final_state(last_entry)

    source_path = last_entry["branch_class"]
    authoritative_receipt_id = last_entry["receipt_id"]
    actionable = final_state != "terminal_failure"

    discarded_paths = [entry["branch_class"] for entry in normalized_chain[:-1]]

    if final_state == "terminal_failure":
        resolution_confidence = "constrained"
    elif source_path == "primary":
        resolution_confidence = "high"
    else:
        resolution_confidence = "bounded"

    resolution_basis = source_path

    instruction = None
    if actionable:
        if final_state in {"success", "retry_resolved", "escalated"}:
            instruction = "downstream_dispatch_permitted"

    case_resolution_id = _make_id("WR-CASE-RESOLUTION")
    created_at = _utc_timestamp()

    return {
        "artifact_type": "case_resolution",
        "payload": {
            "case_resolution_id": case_resolution_id,
            "case_id": case_id,
            "audit_replay_index_id": audit_replay_index_id,
            "created_at": created_at,
            "issuing_authority": issuing_authority,
            "final_state": final_state,
            "source_path": source_path,
            "authoritative_receipt_id": authoritative_receipt_id,
            "payload_class": next(iter(payload_classes)) if len(payload_classes) == 1 else "mixed",
            "route_class": next(iter(route_classes)) if len(route_classes) == 1 else "mixed",
            "execution_mode": next(iter(execution_modes)) if len(execution_modes) == 1 else "mixed",
            "actionable": actionable,
            "instruction": instruction,
            "resolution_basis": resolution_basis,
            "discarded_paths": discarded_paths,
            "resolution_confidence": resolution_confidence,
            "closure_status": "grace_applied",
            "observed_branches": branch_order,
            "replay_chain_length": len(normalized_chain),
            "sealed": True,
        },
    }
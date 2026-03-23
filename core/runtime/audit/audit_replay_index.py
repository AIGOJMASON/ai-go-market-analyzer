from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


APPROVED_RECEIPT_TYPES = {
    "delivery_outcome_receipt": "primary",
    "retry_outcome_receipt": "retry",
    "escalation_outcome_receipt": "escalation",
}

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


class AuditReplayIndexError(ValueError):
    """Raised when Stage 52 audit/replay index construction fails."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:10].upper()}"


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise AuditReplayIndexError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise AuditReplayIndexError(f"{name} must be a dict")
    return value


def _extract_payload(receipt_name: str, receipt: Dict[str, Any]) -> Dict[str, Any]:
    payload = receipt.get("payload")
    if not isinstance(payload, dict):
        raise AuditReplayIndexError(f"{receipt_name}.payload must be a dict")
    return payload


def _require_field(payload: Dict[str, Any], field_name: str, receipt_name: str) -> Any:
    value = payload.get(field_name)
    if value in (None, ""):
        raise AuditReplayIndexError(f"{receipt_name}.payload.{field_name} is required")
    return value


def _normalize_receipt(
    receipt_name: str,
    receipt: Dict[str, Any],
    expected_type: str,
) -> Dict[str, Any]:
    _assert_no_internal_field_leakage(receipt, receipt_name)
    receipt = _require_dict(receipt_name, deepcopy(receipt))

    actual_type = receipt.get("artifact_type")
    if actual_type != expected_type:
        raise AuditReplayIndexError(
            f"{receipt_name}.artifact_type must be {expected_type}, got {actual_type!r}"
        )

    payload = _extract_payload(receipt_name, receipt)

    receipt_id = _require_field(payload, "receipt_id", receipt_name)
    case_id = _require_field(payload, "case_id", receipt_name)
    occurred_at = _require_field(payload, "occurred_at", receipt_name)
    route_class = _require_field(payload, "route_class", receipt_name)
    payload_class = _require_field(payload, "payload_class", receipt_name)
    execution_mode = _require_field(payload, "execution_mode", receipt_name)
    outcome_status = _require_field(payload, "outcome_status", receipt_name)

    branch_class = APPROVED_RECEIPT_TYPES[expected_type]
    declared_branch_class = payload.get("branch_class", branch_class)
    if declared_branch_class != branch_class:
        raise AuditReplayIndexError(
            f"{receipt_name}.payload.branch_class must be {branch_class}, got {declared_branch_class!r}"
        )

    return {
        "receipt_name": receipt_name,
        "artifact_type": actual_type,
        "branch_class": branch_class,
        "receipt_id": receipt_id,
        "case_id": case_id,
        "occurred_at": occurred_at,
        "route_class": route_class,
        "payload_class": payload_class,
        "execution_mode": execution_mode,
        "outcome_status": outcome_status,
        "result_ref": payload.get("result_ref"),
        "source_receipt_ref": payload.get("source_receipt_ref"),
        "adapter_class": payload.get("adapter_class"),
        "adapter_ref": payload.get("adapter_ref"),
        "transport_ref": payload.get("transport_ref"),
        "retry_ref": payload.get("retry_ref"),
        "escalation_ref": payload.get("escalation_ref"),
        "payload_snapshot": deepcopy(payload.get("payload_snapshot")),
    }


def build_audit_replay_index(
    delivery_outcome_receipt: Dict[str, Any],
    retry_outcome_receipt: Optional[Dict[str, Any]] = None,
    escalation_outcome_receipt: Optional[Dict[str, Any]] = None,
    issuing_authority: str = "RUNTIME_AUDIT_REPLAY",
) -> Dict[str, Any]:
    """
    Stage 52 — structural consolidation only.

    Creates a governed audit_replay_index from approved runtime outcome receipts.
    Does not resolve final truth, classify usability, or dispatch downstream.
    """
    normalized_entries: List[Dict[str, Any]] = []

    normalized_entries.append(
        _normalize_receipt(
            receipt_name="delivery_outcome_receipt",
            receipt=delivery_outcome_receipt,
            expected_type="delivery_outcome_receipt",
        )
    )

    if retry_outcome_receipt is not None:
        normalized_entries.append(
            _normalize_receipt(
                receipt_name="retry_outcome_receipt",
                receipt=retry_outcome_receipt,
                expected_type="retry_outcome_receipt",
            )
        )

    if escalation_outcome_receipt is not None:
        normalized_entries.append(
            _normalize_receipt(
                receipt_name="escalation_outcome_receipt",
                receipt=escalation_outcome_receipt,
                expected_type="escalation_outcome_receipt",
            )
        )

    case_ids = {entry["case_id"] for entry in normalized_entries}
    if len(case_ids) != 1:
        raise AuditReplayIndexError("all provided receipts must share the same case_id")

    branch_classes = [entry["branch_class"] for entry in normalized_entries]
    if len(branch_classes) != len(set(branch_classes)):
        raise AuditReplayIndexError("duplicate branch_class detected in replay inputs")

    route_classes = {entry["route_class"] for entry in normalized_entries}
    payload_classes = {entry["payload_class"] for entry in normalized_entries}
    execution_modes = {entry["execution_mode"] for entry in normalized_entries}

    replay_chain: List[Dict[str, Any]] = []
    for sequence, entry in enumerate(normalized_entries, start=1):
        replay_chain.append(
            {
                "sequence": sequence,
                "branch_class": entry["branch_class"],
                "artifact_type": entry["artifact_type"],
                "receipt_id": entry["receipt_id"],
                "occurred_at": entry["occurred_at"],
                "outcome_status": entry["outcome_status"],
                "route_class": entry["route_class"],
                "payload_class": entry["payload_class"],
                "execution_mode": entry["execution_mode"],
                "result_ref": entry["result_ref"],
                "source_receipt_ref": entry["source_receipt_ref"],
                "adapter_class": entry["adapter_class"],
                "adapter_ref": entry["adapter_ref"],
                "transport_ref": entry["transport_ref"],
                "retry_ref": entry["retry_ref"],
                "escalation_ref": entry["escalation_ref"],
                "payload_snapshot": entry["payload_snapshot"],
            }
        )

    case_id = next(iter(case_ids))
    audit_replay_index_id = _make_id("WR-AUDIT-REPLAY")
    created_at = _utc_timestamp()

    replay_refs = {
        "delivery_outcome_receipt_id": normalized_entries[0]["receipt_id"],
        "retry_outcome_receipt_id": None,
        "escalation_outcome_receipt_id": None,
    }
    for entry in normalized_entries:
        if entry["branch_class"] == "retry":
            replay_refs["retry_outcome_receipt_id"] = entry["receipt_id"]
        elif entry["branch_class"] == "escalation":
            replay_refs["escalation_outcome_receipt_id"] = entry["receipt_id"]

    return {
        "artifact_type": "audit_replay_index",
        "payload": {
            "audit_replay_index_id": audit_replay_index_id,
            "case_id": case_id,
            "created_at": created_at,
            "issuing_authority": issuing_authority,
            "replay_chain": replay_chain,
            "replay_order": [entry["receipt_id"] for entry in normalized_entries],
            "replay_refs": replay_refs,
            "observed_branches": branch_classes,
            "latest_receipt_id": normalized_entries[-1]["receipt_id"],
            "route_class": next(iter(route_classes)) if len(route_classes) == 1 else "mixed",
            "payload_class": next(iter(payload_classes)) if len(payload_classes) == 1 else "mixed",
            "execution_mode": next(iter(execution_modes)) if len(execution_modes) == 1 else "mixed",
            "branch_count": len(normalized_entries),
            "trace_complete": True,
            "resolution_pending": True,
            "sealed": True,
        },
    }
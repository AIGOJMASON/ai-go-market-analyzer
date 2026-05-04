# AI_GO/child_cores/contractor_builder_v1/decision_log/decision_receipt_builder.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
except ModuleNotFoundError:
    from core.receipts.receipt_writer import write_contractor_receipt


DECLARED_DECISION_EVENTS = {
    "create_decision",
    "submit_decision",
    "review_decision",
    "approve_decision",
    "reject_decision",
    "change_decision_status",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def build_decision_receipt(
    *,
    event_type: str,
    project_id: str,
    decision_id: str,
    artifact_path: str,
    actor: str = "system",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event_type_clean = _required(event_type, "event_type")

    if event_type_clean not in DECLARED_DECISION_EVENTS:
        raise ValueError(f"Undeclared decision receipt event: {event_type_clean}")

    return {
        "module_id": "decision_log",
        "event_type": event_type_clean,
        "generated_at": _utc_now_iso(),
        "project_id": _required(project_id, "project_id"),
        "decision_id": _required(decision_id, "decision_id"),
        "artifact_path": _required(artifact_path, "artifact_path"),
        "actor": str(actor or "system").strip() or "system",
        "details": dict(details or {}),
    }


def write_decision_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    result = write_contractor_receipt(
        module_name="decision_log",
        event_type=str(receipt.get("event_type", "decision_event")),
        receipt=receipt,
        project_id=str(receipt.get("project_id", "")).strip() or None,
        write_project_copy=False,
    )
    return Path(result["global_path"])
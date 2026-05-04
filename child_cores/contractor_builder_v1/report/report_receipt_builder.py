# AI_GO/child_cores/contractor_builder_v1/report/report_receipt_builder.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
except ModuleNotFoundError:
    from core.receipts.receipt_writer import write_contractor_receipt


DECLARED_REPORT_EVENTS = {
    "generate_project_weekly",
    "generate_portfolio_weekly",
    "approve_report",
    "archive_report",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def build_report_receipt(
    *,
    event_type: str,
    subject_id: str,
    report_id: str,
    artifact_path: str,
    actor: str = "system",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event_type_clean = _required(event_type, "event_type")

    if event_type_clean not in DECLARED_REPORT_EVENTS:
        raise ValueError(f"Undeclared report receipt event: {event_type_clean}")

    return {
        "module_id": "report",
        "event_type": event_type_clean,
        "generated_at": _utc_now_iso(),
        "subject_id": _required(subject_id, "subject_id"),
        "report_id": _required(report_id, "report_id"),
        "artifact_path": _required(artifact_path, "artifact_path"),
        "actor": str(actor or "system").strip() or "system",
        "details": dict(details or {}),
    }


def write_report_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    project_id = str(receipt.get("project_id") or receipt.get("subject_id") or "").strip()

    result = write_contractor_receipt(
        module_name="report",
        event_type=str(receipt.get("event_type", "report_event")),
        receipt=receipt,
        project_id=project_id or None,
        write_project_copy=False,
    )
    return Path(result["global_path"])
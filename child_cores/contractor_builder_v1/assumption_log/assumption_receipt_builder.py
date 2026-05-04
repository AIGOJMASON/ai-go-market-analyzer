# AI_GO/child_cores/contractor_builder_v1/assumption_log/assumption_receipt_builder.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
except ModuleNotFoundError:
    from core.receipts.receipt_writer import write_contractor_receipt


DECLARED_ASSUMPTION_EVENTS = {
    "create_assumption",
    "change_assumption_status",
    "invalidate_assumption",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def build_assumption_receipt(
    *,
    event_type: str,
    project_id: str,
    assumption_id: str,
    artifact_path: str,
    actor: str = "system",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event_type_clean = _required(event_type, "event_type")

    if event_type_clean not in DECLARED_ASSUMPTION_EVENTS:
        raise ValueError(f"Undeclared assumption receipt event: {event_type_clean}")

    return {
        "module_id": "assumption_log",
        "event_type": event_type_clean,
        "generated_at": _utc_now_iso(),
        "project_id": _required(project_id, "project_id"),
        "assumption_id": _required(assumption_id, "assumption_id"),
        "artifact_path": _required(artifact_path, "artifact_path"),
        "actor": str(actor or "system").strip() or "system",
        "details": dict(details or {}),
    }


def write_assumption_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    result = write_contractor_receipt(
        module_name="assumption_log",
        event_type=str(receipt.get("event_type", "assumption_event")),
        receipt=receipt,
        project_id=str(receipt.get("project_id", "")).strip() or None,
        write_project_copy=False,
    )
    return Path(result["global_path"])
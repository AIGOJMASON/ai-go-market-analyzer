# AI_GO/child_cores/contractor_builder_v1/documents/pdf_receipt_builder.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
except ModuleNotFoundError:
    from core.receipts.receipt_writer import write_contractor_receipt


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def build_pdf_receipt(
    *,
    event_type: str,
    project_id: str,
    phase_id: str,
    artifact_path: str,
    artifact_id: str,
    pdf_hash: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "module_id": "documents",
        "event_type": _required(event_type, "event_type"),
        "generated_at": _utc_now_iso(),
        "project_id": _required(project_id, "project_id"),
        "phase_id": _required(phase_id, "phase_id"),
        "artifact_id": _required(artifact_id, "artifact_id"),
        "artifact_path": _required(artifact_path, "artifact_path"),
        "pdf_hash": _required(pdf_hash, "pdf_hash"),
        "details": dict(details or {}),
    }


def write_pdf_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    result = write_contractor_receipt(
        module_name="documents",
        event_type=str(receipt.get("event_type", "document_event")),
        receipt=receipt,
        project_id=str(receipt.get("project_id", "")).strip() or None,
        write_project_copy=False,
    )

    return Path(result["global_path"])
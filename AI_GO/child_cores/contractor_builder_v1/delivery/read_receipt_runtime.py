"""
Read receipt runtime for contractor_builder_v1.

This module records best-effort open/read evidence for delivered phase-closeout
emails. Open evidence is informative only. Signed acknowledgment remains the
governing event.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_read_receipt_event(
    *,
    delivery_id: str,
    project_id: str,
    phase_id: str,
    recipient_email: str,
    opened_at: str | None = None,
    provider_event_id: str = "",
) -> Dict[str, Any]:
    return {
        "delivery_id": delivery_id,
        "project_id": project_id,
        "phase_id": phase_id,
        "recipient_email": recipient_email,
        "opened_at": opened_at or _utc_now_iso(),
        "provider_event_id": provider_event_id,
        "event_type": "opened",
    }


def mark_email_opened(record: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(record)
    updated["read_receipt_status"] = "opened"
    updated["opened_at"] = _utc_now_iso()
    return updated
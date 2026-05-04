"""
Risk review runtime for contractor_builder_v1.

This module handles weekly review posture for risk entries. It does not score risk.
It records review state and flags whether review is due.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Dict


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def risk_requires_review(entry: Dict[str, Any], *, now: datetime | None = None) -> bool:
    """
    Return True if a risk should be reviewed.

    Current policy:
    - weekly review means review due if last_reviewed is missing or older than 7 days
    - non-weekly values default to requiring review when last_reviewed is missing
    """
    now = now or _utc_now()
    review_frequency = str(entry.get("review_frequency", "weekly")).lower().strip()
    last_reviewed = str(entry.get("last_reviewed", "") or "").strip()

    if not last_reviewed:
        return True

    try:
        parsed = datetime.fromisoformat(last_reviewed)
    except ValueError:
        return True

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    if review_frequency == "weekly":
        return parsed <= (now - timedelta(days=7))

    return False


def build_risk_review_record(
    *,
    project_id: str,
    risk_id: str,
    reviewer_name: str,
    reviewer_role: str,
    previous_status: str,
    current_status: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a review event record for a risk entry.
    """
    return {
        "generated_at": _utc_now_iso(),
        "project_id": project_id,
        "risk_id": risk_id,
        "reviewer_name": reviewer_name,
        "reviewer_role": reviewer_role,
        "previous_status": previous_status,
        "current_status": current_status,
        "notes": notes,
    }


def review_risk_entry(
    entry: Dict[str, Any],
    *,
    reviewer_name: str,
    reviewer_role: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Return a copy of the risk entry with last_reviewed refreshed and optional notes appended.
    """
    updated = dict(entry)
    updated["last_reviewed"] = _utc_now_iso()

    existing_notes = str(updated.get("notes", "") or "")
    if notes:
        updated["notes"] = (
            existing_notes + ("\n" if existing_notes else "") + notes
        )

    return updated
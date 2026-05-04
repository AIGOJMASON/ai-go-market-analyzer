"""
Approval runtime for contractor_builder_v1 reports.

This module enforces PM-gated approval posture for reports.
It does not auto-release and does not mutate upstream data.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def can_approve_report(report: Dict[str, Any]) -> bool:
    """
    A report may be approved only from pm_review when deterministic block exists.
    """
    if report.get("report_status") != "pm_review":
        return False
    deterministic_block = report.get("deterministic_block", {})
    return isinstance(deterministic_block, dict) and len(deterministic_block) > 0


def can_archive_report(report: Dict[str, Any]) -> bool:
    """
    A report may be archived only after approval.
    """
    return report.get("report_status") == "approved"


def apply_report_pm_approval(
    report: Dict[str, Any],
    *,
    approved_by: str,
    signature: str,
    approval_notes: str = "",
) -> Dict[str, Any]:
    """
    Apply PM approval metadata to a report.
    """
    updated = dict(report)
    updated["pm_approval"] = {
        "approved_by": approved_by,
        "approved_at": _utc_now_iso(),
        "approval_notes": approval_notes,
        "signature": signature,
    }
    return updated


def transition_report_status(
    report: Dict[str, Any],
    *,
    new_status: str,
) -> Dict[str, Any]:
    """
    Return a copy of a report with updated status.
    """
    updated = dict(report)
    updated["report_status"] = new_status
    return updated
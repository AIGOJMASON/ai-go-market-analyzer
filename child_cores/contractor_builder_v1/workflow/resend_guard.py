from __future__ import annotations

from typing import Any


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def can_resend(latest_status: str, workflow_status: str) -> bool:
    """
    Determine whether a signoff resend is allowed.

    Guard posture:
    - resend is allowed for declined or active sent posture
    - resend is not allowed for signed posture
    - resend is not allowed once workflow is complete unless the phase has already
      been reopened/blocked by workflow authority
    """
    latest_status_clean = _normalize_text(latest_status)
    workflow_status_clean = _normalize_text(workflow_status)

    if latest_status_clean == "signed":
        return False

    if latest_status_clean in {"declined", "sent"}:
        if workflow_status_clean == "complete" and latest_status_clean != "declined":
            return False
        return True

    return False
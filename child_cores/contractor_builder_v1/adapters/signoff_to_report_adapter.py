"""
Signoff to report adapter for contractor_builder_v1.

This adapter translates client signoff status records into the bounded structure
expected by report consumers.

Authority rule:
- It may read signoff status fields.
- It may not infer workflow state.
- It may not advance phases.
- It may not decide whether signoff is valid.
"""

from __future__ import annotations

from typing import Any, Dict


def _clean(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def build_signoff_report_snapshot(
    *,
    signoff_status: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(signoff_status, dict):
        signoff_status = {}

    return {
        "project_id": _clean(signoff_status.get("project_id")),
        "phase_id": _clean(signoff_status.get("phase_id")),
        "status": _clean(signoff_status.get("status"), default="not_requested"),
        "client_name": _clean(signoff_status.get("client_name")),
        "client_email": _clean(signoff_status.get("client_email")),
        "pdf_artifact_id": signoff_status.get("pdf_artifact_id"),
        "sent_at": signoff_status.get("sent_at"),
        "opened_at": signoff_status.get("opened_at"),
        "signed_at": signoff_status.get("signed_at"),
        "declined_at": signoff_status.get("declined_at"),
    }
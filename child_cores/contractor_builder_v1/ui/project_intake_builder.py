"""
Project intake builder for contractor_builder_v1.

This module shapes the created project record into the response view model returned
by the intake runner/API after successful Stage 1 creation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_project_intake_created_view(
    *,
    project_record_view: Dict[str, Any],
    message: str = "Project created successfully.",
) -> Dict[str, Any]:
    identity_panel = dict(project_record_view.get("identity_panel", {}))
    baseline_panel = dict(project_record_view.get("baseline_panel", {}))

    return {
        "status": "created",
        "generated_at": _utc_now_iso(),
        "message": message,
        "summary_panel": {
            "project_id": identity_panel.get("project_id", ""),
            "project_name": identity_panel.get("project_name", ""),
            "project_type": identity_panel.get("project_type", ""),
            "client_name": identity_panel.get("client_name", ""),
            "pm_name": identity_panel.get("pm_name", ""),
            "state": dict(identity_panel.get("jurisdiction", {})).get("state", ""),
            "baseline_locked": baseline_panel.get("lock_status", "") == "locked",
        },
        "project_record": project_record_view,
    }
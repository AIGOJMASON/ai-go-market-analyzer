"""
Phase closeout explainer for contractor_builder_v1.

This module builds bounded customer-facing closeout messaging from canonical
phase and workflow data only.

It does NOT:
- invent facts
- infer approvals
- mutate workflow truth
- decide readiness
"""

from __future__ import annotations

from typing import Any, Dict

from .email_template_renderer import render_phase_closeout_email


def _normalize_text(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def build_phase_closeout_subject(
    *,
    phase_name: str,
    project_name: str = "",
    project_id: str = "",
) -> str:
    rendered = render_phase_closeout_email(
        {
            "project_name": _normalize_text(project_name),
            "project_id": _normalize_text(project_id),
            "phase_name": _normalize_text(phase_name, default="Project Phase"),
        }
    )
    return rendered["subject"]


def build_phase_closeout_body(
    *,
    project_id: str,
    phase_id: str,
    phase_name: str,
    checklist_summary: Dict[str, Any],
    project_name: str = "",
) -> str:
    rendered = render_phase_closeout_email(
        {
            "project_name": _normalize_text(project_name),
            "project_id": _normalize_text(project_id),
            "phase_name": _normalize_text(phase_name, default=phase_id),
            "phase_id": _normalize_text(phase_id),
            "checklist_summary": dict(checklist_summary or {}),
        }
    )
    return rendered["body"]
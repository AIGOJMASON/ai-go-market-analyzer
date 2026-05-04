from __future__ import annotations

from typing import Any, Dict


def _normalize_text(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in {"true", "True", "1", 1}:
        return True
    if value in {"false", "False", "0", 0}:
        return False
    return default


def render_phase_closeout_email(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Render a bounded customer-facing phase closeout email.

    This renderer is intentionally presentation-only:
    - it maps already-structured canonical data into readable email content
    - it does not infer approvals, readiness, or workflow authority
    """
    project_name = _normalize_text(
        data.get("project_name"),
        default=_normalize_text(data.get("project_id"), default="Project"),
    )
    project_id = _normalize_text(data.get("project_id"))
    phase_name = _normalize_text(
        data.get("phase_name"),
        default=_normalize_text(data.get("phase_id"), default="Project Phase"),
    )
    phase_id = _normalize_text(data.get("phase_id"))
    checklist_summary = dict(data.get("checklist_summary", {}))

    required_item_count = _coerce_int(
        checklist_summary.get("required_item_count"),
        default=_coerce_int(checklist_summary.get("required"), default=0),
    )
    completed_required_count = _coerce_int(
        checklist_summary.get("completed_required_count"),
        default=_coerce_int(checklist_summary.get("completed"), default=0),
    )
    ready_for_signoff = _coerce_bool(
        checklist_summary.get("ready_for_signoff"),
        default=_coerce_bool(checklist_summary.get("ready"), default=False),
    )

    subject = f"Action Required: {project_name} - {phase_name} Signoff"

    body_lines = [
        f"Project Overview",
        f"Project: {project_name}",
        f"Project ID: {project_id}",
        "",
        f"Phase Summary",
        f"Phase: {phase_name}",
        f"Phase ID: {phase_id}",
        "",
        f"Checklist Status",
        f"- Required checklist items: {required_item_count}",
        f"- Completed required items: {completed_required_count}",
        f"- Ready for signoff: {'Yes' if ready_for_signoff else 'No'}",
        "",
        "Action Required",
        "Please review the attached phase closeout document and approve or decline this phase.",
        "",
        "What Happens Next",
        "- If approved, the project may move forward under the governed workflow.",
        "- If declined, the phase will reopen for correction and workflow will remain controlled.",
        "",
        "This message was generated from the canonical project record.",
    ]

    return {
        "subject": subject.strip(),
        "body": "\n".join(body_lines).strip(),
    }
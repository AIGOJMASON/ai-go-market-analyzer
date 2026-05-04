from __future__ import annotations

from typing import Any, Dict

from ..workflow.resend_guard import can_resend


def _normalize_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


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


def _derive_recommended_action(
    *,
    workflow_status: str,
    phase_signoff_status: str,
    delivery_status: str,
    resend_allowed: bool,
) -> str:
    if phase_signoff_status == "declined":
        return "review_decline"
    if delivery_status == "failed" and resend_allowed:
        return "resend"
    if phase_signoff_status == "sent":
        return "wait"
    if workflow_status == "complete" or phase_signoff_status == "signed":
        return "none"
    return "review"


def enrich_dashboard(
    *,
    operator_payload: Dict[str, Any],
    phase_signoff_status: str,
    checklist_summary: Dict[str, Any] | None = None,
    latest_delivery_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Add visibility-only dashboard polish blocks.

    This function is read-only enrichment:
    - it summarizes signoff and delivery posture
    - it does not mutate workflow, signoff, or delivery truth
    """
    payload = dict(operator_payload or {})

    summary_panel = _normalize_mapping(payload.get("summary_panel"))
    project_panel = _normalize_mapping(payload.get("project_panel"))
    workflow = _normalize_mapping(project_panel.get("workflow"))
    checklist_summary_clean = _normalize_mapping(checklist_summary)
    delivery_record = _normalize_mapping(latest_delivery_record)

    workflow_status = _normalize_text(
        workflow.get("workflow_status"),
        default=_normalize_text(summary_panel.get("workflow_status"), default=""),
    )
    phase_signoff_status_clean = _normalize_text(
        phase_signoff_status,
        default=_normalize_text(project_panel.get("phase_signoff_status"), default="not_requested"),
    )

    delivery_status = _normalize_text(
        delivery_record.get("delivery_status", delivery_record.get("status", "")),
        default="unknown",
    )

    resend_allowed = can_resend(
        latest_status=phase_signoff_status_clean,
        workflow_status=workflow_status,
    )

    signoff_summary = {
        "latest_status": phase_signoff_status_clean,
        "phase_posture": (
            "complete"
            if workflow_status == "complete" or phase_signoff_status_clean == "signed"
            else "awaiting_signoff"
            if phase_signoff_status_clean in {"sent", "declined", "not_requested"}
            else workflow_status
        ),
        "checklist_summary": {
            "required_item_count": _coerce_int(checklist_summary_clean.get("required_item_count")),
            "completed_required_count": _coerce_int(checklist_summary_clean.get("completed_required_count")),
            "ready_for_signoff": _coerce_bool(checklist_summary_clean.get("ready_for_signoff")),
            "phase_id": _normalize_text(checklist_summary_clean.get("phase_id")),
        },
        "resend_allowed": resend_allowed,
        "recommended_action": _derive_recommended_action(
            workflow_status=workflow_status,
            phase_signoff_status=phase_signoff_status_clean,
            delivery_status=delivery_status,
            resend_allowed=resend_allowed,
        ),
    }

    delivery_summary = {
        "delivery_status": delivery_status,
        "delivery_id": _normalize_text(delivery_record.get("delivery_id")),
        "sent_at": _normalize_text(delivery_record.get("sent_at")),
        "recipient": _normalize_text(delivery_record.get("recipient_email", delivery_record.get("recipient", ""))),
        "attachment": _normalize_text(delivery_record.get("attachment_path", delivery_record.get("attachment", ""))),
        "error": _normalize_text(delivery_record.get("error")),
        "provider": _normalize_text(delivery_record.get("provider")),
        "retry_recommended": delivery_status == "failed" and resend_allowed,
    }

    payload["signoff_summary_panel"] = signoff_summary
    payload["delivery_summary_panel"] = delivery_summary
    return payload
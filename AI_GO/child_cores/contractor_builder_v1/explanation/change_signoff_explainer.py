"""
Change signoff explainer for contractor_builder_v1.

This module builds bounded customer-facing change-signoff messaging from canonical
change packet data only.

It does NOT:
- invent facts
- infer approvals
- mutate change truth
- decide workflow or closeout authority
"""

from __future__ import annotations

from typing import Any, Dict

from ..change.change_signoff_policy import build_change_signoff_policy_summary


def _normalize_text(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _coerce_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def build_change_signoff_subject(
    *,
    packet: Dict[str, Any],
    project_name: str = "",
    phase_name: str = "",
) -> str:
    packet_clean = dict(packet or {})
    project_label = _normalize_text(
        project_name,
        default=_normalize_text(packet_clean.get("project_id"), default="Project"),
    )
    title = _normalize_text(packet_clean.get("title"), default="Change Request")
    phase_label = _normalize_text(
        phase_name,
        default=_normalize_text(packet_clean.get("phase_id"), default="Project Phase"),
    )

    return f"Action Required: {project_label} - {phase_label} - {title}"


def build_change_signoff_body(
    *,
    packet: Dict[str, Any],
    project_name: str = "",
    phase_name: str = "",
    latest_signoff_status: Dict[str, Any] | None = None,
) -> str:
    packet_clean = dict(packet or {})
    policy_summary = build_change_signoff_policy_summary(
        packet_clean,
        latest_signoff_status=latest_signoff_status,
    )

    project_label = _normalize_text(
        project_name,
        default=_normalize_text(packet_clean.get("project_id"), default="Project"),
    )
    phase_label = _normalize_text(
        phase_name,
        default=_normalize_text(packet_clean.get("phase_id"), default="Project Phase"),
    )
    title = _normalize_text(packet_clean.get("title"), default="Change Request")
    change_packet_id = _normalize_text(packet_clean.get("change_packet_id"))
    scope_delta = dict(packet_clean.get("scope_delta", {}))
    description = _normalize_text(scope_delta.get("description"))
    cost_total = _coerce_float(policy_summary.get("cost_delta_total"))
    schedule_total_days = _coerce_float(policy_summary.get("schedule_delta_total_days"))

    body_lines = [
        "Change Request Overview",
        f"Project: {project_label}",
        f"Phase: {phase_label}",
        f"Change Title: {title}",
        f"Change Packet ID: {change_packet_id}",
        "",
        "Requested Change",
        description or "No additional change description was provided.",
        "",
        "Deterministic Impact Summary",
        f"- Estimated cost delta: {cost_total:.2f}",
        f"- Estimated schedule delta days: {schedule_total_days:.2f}",
        f"- Customer signoff required: {'Yes' if policy_summary['requires_customer_signoff'] else 'No'}",
        "",
        "Action Required",
        "Please review this requested project change and approve or decline it.",
        "",
        "What Happens Next",
        "- If approved, the change may proceed through the governed contractor workflow.",
        "- If declined, the change remains unresolved and may block related phase closeout until corrected or superseded.",
        "",
        "This message was generated from the canonical project and change records.",
    ]

    return "\n".join(body_lines).strip()
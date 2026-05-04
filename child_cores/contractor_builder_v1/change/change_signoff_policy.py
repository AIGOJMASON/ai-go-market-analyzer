"""
Change signoff policy for contractor_builder_v1.

This module classifies whether a change packet:
- requires customer signoff
- blocks phase closeout while unresolved
- is already resolved for closeout purposes

It is deterministic and reads only structured change packet fields.
It does NOT:
- mutate packet state
- send communication
- approve changes
- replace workflow authority
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


RESOLVED_CHANGE_PACKET_STATUSES = {"rejected", "archived"}
UNRESOLVED_SIGNOFF_STATUSES = {"not_requested", "sent", "declined"}


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


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in {"true", "True", "1", 1}:
        return True
    if value in {"false", "False", "0", 0}:
        return False
    return default


def _normalize_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return list(value)
    return []


def _explicit_customer_impact(packet: Dict[str, Any]) -> Dict[str, Any]:
    customer_impact = packet.get("customer_impact", {})
    if isinstance(customer_impact, dict):
        return dict(customer_impact)
    return {}


def _packet_status(packet: Dict[str, Any]) -> str:
    return _normalize_text(packet.get("status"))


def _scope_delta(packet: Dict[str, Any]) -> Dict[str, Any]:
    value = packet.get("scope_delta", {})
    if isinstance(value, dict):
        return dict(value)
    return {}


def _deterministic_block(packet: Dict[str, Any]) -> Dict[str, Any]:
    value = packet.get("deterministic_block", {})
    if isinstance(value, dict):
        return dict(value)
    return {}


def _cost_delta(packet: Dict[str, Any]) -> Dict[str, Any]:
    value = _deterministic_block(packet).get("cost_delta", {})
    if isinstance(value, dict):
        return dict(value)
    return {}


def _time_delta(packet: Dict[str, Any]) -> Dict[str, Any]:
    value = _deterministic_block(packet).get("time_delta", {})
    if isinstance(value, dict):
        return dict(value)
    return {}


def _infer_requires_customer_signoff(packet: Dict[str, Any]) -> tuple[bool, List[str]]:
    reasons: List[str] = []

    scope_delta = _scope_delta(packet)
    added_items = _normalize_list(scope_delta.get("added_items"))
    removed_items = _normalize_list(scope_delta.get("removed_items"))
    scope_description = _normalize_text(scope_delta.get("description"))
    scope_notes = _normalize_text(scope_delta.get("notes"))

    total_change_order_amount = _coerce_float(
        _cost_delta(packet).get("total_change_order_amount")
    )
    total_schedule_delta_days = _coerce_float(
        _time_delta(packet).get("total_schedule_delta_days")
    )

    if added_items or removed_items:
        reasons.append("scope_items_changed")

    if scope_description and scope_description.lower() not in {"n/a", "none"}:
        reasons.append("scope_description_present")

    if scope_notes:
        reasons.append("scope_notes_present")

    if abs(total_change_order_amount) > 0:
        reasons.append("cost_delta_present")

    if abs(total_schedule_delta_days) > 0:
        reasons.append("schedule_delta_present")

    return (len(reasons) > 0, reasons)


def build_change_signoff_policy_summary(
    packet: Dict[str, Any],
    latest_signoff_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a deterministic policy summary for one change packet.
    """
    packet_clean = dict(packet or {})
    explicit_customer_impact = _explicit_customer_impact(packet_clean)

    explicit_requires = explicit_customer_impact.get("requires_customer_signoff")
    explicit_blocks = explicit_customer_impact.get("blocks_phase_closeout_when_unresolved")
    explicit_reason = _normalize_text(explicit_customer_impact.get("impact_reason"))
    explicit_summary = _normalize_text(explicit_customer_impact.get("customer_visible_summary"))

    inferred_requires, inferred_reasons = _infer_requires_customer_signoff(packet_clean)

    requires_customer_signoff = (
        _coerce_bool(explicit_requires)
        if explicit_requires is not None
        else inferred_requires
    )

    blocks_phase_closeout_when_unresolved = (
        _coerce_bool(explicit_blocks)
        if explicit_blocks is not None
        else requires_customer_signoff
    )

    status_value = (
        _normalize_text((latest_signoff_status or {}).get("status"))
        if latest_signoff_status
        else "not_requested"
    )

    packet_status = _packet_status(packet_clean)

    signoff_resolved = (
        False
        if not requires_customer_signoff
        else status_value == "signed"
    )

    closed_without_release = packet_status in RESOLVED_CHANGE_PACKET_STATUSES

    is_blocking_unresolved = (
        requires_customer_signoff
        and blocks_phase_closeout_when_unresolved
        and not signoff_resolved
        and not closed_without_release
        and status_value in UNRESOLVED_SIGNOFF_STATUSES
    )

    impact_reason = explicit_reason or ", ".join(inferred_reasons)
    customer_visible_summary = explicit_summary or _normalize_text(
        packet_clean.get("title"),
        default=_normalize_text(_scope_delta(packet_clean).get("description"), default="Change request"),
    )

    return {
        "project_id": _normalize_text(packet_clean.get("project_id")),
        "phase_id": _normalize_text(packet_clean.get("phase_id")),
        "change_packet_id": _normalize_text(packet_clean.get("change_packet_id")),
        "packet_status": packet_status,
        "requires_customer_signoff": requires_customer_signoff,
        "blocks_phase_closeout_when_unresolved": blocks_phase_closeout_when_unresolved,
        "signoff_resolved": signoff_resolved,
        "latest_signoff_status": status_value,
        "closed_without_release": closed_without_release,
        "is_blocking_unresolved": is_blocking_unresolved,
        "impact_reason": impact_reason,
        "customer_visible_summary": customer_visible_summary,
        "inferred_reasons": inferred_reasons,
        "cost_delta_total": _coerce_float(
            _cost_delta(packet_clean).get("total_change_order_amount")
        ),
        "schedule_delta_total_days": _coerce_float(
            _time_delta(packet_clean).get("total_schedule_delta_days")
        ),
    }


def change_requires_customer_signoff(packet: Dict[str, Any]) -> bool:
    """
    Convenience helper returning only the signoff-required decision.
    """
    return bool(build_change_signoff_policy_summary(packet)["requires_customer_signoff"])


def is_change_signoff_resolved(
    packet: Dict[str, Any],
    latest_signoff_status: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Convenience helper returning whether change signoff is resolved.
    """
    return bool(
        build_change_signoff_policy_summary(
            packet,
            latest_signoff_status=latest_signoff_status,
        )["signoff_resolved"]
    )


def is_blocking_unresolved_change(
    packet: Dict[str, Any],
    latest_signoff_status: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Convenience helper returning whether the change should block closeout.
    """
    return bool(
        build_change_signoff_policy_summary(
            packet,
            latest_signoff_status=latest_signoff_status,
        )["is_blocking_unresolved"]
    )
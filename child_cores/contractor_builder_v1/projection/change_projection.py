"""
Change projection for contractor_builder_v1.

This module builds a bounded change summary panel from change packet records.

Projection is read-only and visibility-only.
It does NOT:
- mutate change truth
- infer approvals outside structured fields
- replace change or workflow authority
"""

from __future__ import annotations

from typing import Any, Dict, List


def _normalize_list_of_mappings(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _normalize_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _coerce_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _cost_delta_total(record: Dict[str, Any]) -> float:
    return _coerce_float(
        _normalize_mapping(
            _normalize_mapping(record.get("deterministic_block", {})).get("cost_delta", {})
        ).get("total_change_order_amount")
    )


def _schedule_delta_total(record: Dict[str, Any]) -> float:
    return _coerce_float(
        _normalize_mapping(
            _normalize_mapping(record.get("deterministic_block", {})).get("time_delta", {})
        ).get("total_schedule_delta_days")
    )


def _customer_impact(record: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_mapping(record.get("customer_impact", {}))


def _change_signoff(record: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_mapping(record.get("change_signoff", {}))


def _requires_customer_signoff(record: Dict[str, Any]) -> bool:
    value = _customer_impact(record).get("requires_customer_signoff")
    return value is True


def _blocks_closeout_when_unresolved(record: Dict[str, Any]) -> bool:
    value = _customer_impact(record).get("blocks_phase_closeout_when_unresolved")
    return value is True


def _latest_signoff_status(record: Dict[str, Any]) -> str:
    return str(_change_signoff(record).get("status", "")).strip() or "not_requested"


def _is_blocking_unresolved(record: Dict[str, Any]) -> bool:
    latest_status = _latest_signoff_status(record)
    packet_status = str(record.get("status", "")).strip()

    if packet_status in {"rejected", "archived"}:
        return False

    return (
        _requires_customer_signoff(record)
        and _blocks_closeout_when_unresolved(record)
        and latest_status != "signed"
    )


def build_change_projection(
    *,
    change_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded changes panel.
    """
    records = _normalize_list_of_mappings(change_records)

    approved_change_count = sum(
        1 for record in records
        if str(record.get("status", "")).strip() == "approved"
    )
    pending_approval_count = sum(
        1 for record in records
        if str(record.get("status", "")).strip() == "pending_approvals"
    )
    customer_signoff_required_count = sum(
        1 for record in records if _requires_customer_signoff(record)
    )
    blocking_unresolved_change_count = sum(
        1 for record in records if _is_blocking_unresolved(record)
    )

    approved_total_amount = round(
        sum(
            _cost_delta_total(record)
            for record in records
            if str(record.get("status", "")).strip() == "approved"
        ),
        2,
    )

    latest_items = [
        {
            "change_packet_id": str(record.get("change_packet_id", "")).strip(),
            "title": str(record.get("title", "")).strip(),
            "status": str(record.get("status", "")).strip(),
            "phase_id": str(record.get("phase_id", "")).strip(),
            "requires_customer_signoff": _requires_customer_signoff(record),
            "blocks_phase_closeout_when_unresolved": _blocks_closeout_when_unresolved(record),
            "latest_signoff_status": _latest_signoff_status(record),
            "is_blocking_unresolved": _is_blocking_unresolved(record),
            "impact_reason": str(_customer_impact(record).get("impact_reason", "")).strip(),
            "customer_visible_summary": str(
                _customer_impact(record).get("customer_visible_summary", "")
            ).strip(),
            "total_change_order_amount": _cost_delta_total(record),
            "total_schedule_delta_days": _schedule_delta_total(record),
        }
        for record in records[-5:]
    ]

    blocking_items = [
        item for item in latest_items if bool(item.get("is_blocking_unresolved"))
    ]

    return {
        "change_count": len(records),
        "approved_change_count": approved_change_count,
        "pending_approval_count": pending_approval_count,
        "customer_signoff_required_count": customer_signoff_required_count,
        "blocking_unresolved_change_count": blocking_unresolved_change_count,
        "has_blocking_unresolved_changes": blocking_unresolved_change_count > 0,
        "approved_change_total_amount": approved_total_amount,
        "latest_items": latest_items,
        "blocking_items": blocking_items,
    }
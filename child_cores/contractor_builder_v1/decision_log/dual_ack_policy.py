"""
Dual acknowledgment policy for contractor_builder_v1 decisions.

This module enforces simple lawful signature and status readiness checks for
internal decision governance.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def apply_requester_signature(
    entry: Dict[str, Any],
    *,
    name: str,
    role: str,
    org: str,
    signature: str,
) -> Dict[str, Any]:
    """
    Apply requester identity and signature to a decision entry.
    """
    updated = dict(entry)
    requested_by = dict(updated.get("requested_by", {}))
    requested_by.update(
        {
            "name": name,
            "role": role,
            "org": org,
            "signature": signature,
            "timestamp": _utc_now_iso(),
        }
    )
    updated["requested_by"] = requested_by
    return updated


def apply_approver_signature(
    entry: Dict[str, Any],
    *,
    name: str,
    role: str,
    org: str,
    signature: str,
) -> Dict[str, Any]:
    """
    Apply approver identity and signature to a decision entry.
    """
    updated = dict(entry)
    approved_by = dict(updated.get("approved_by", {}))
    approved_by.update(
        {
            "name": name,
            "role": role,
            "org": org,
            "signature": signature,
            "timestamp": _utc_now_iso(),
        }
    )
    updated["approved_by"] = approved_by
    return updated


def can_submit_decision(entry: Dict[str, Any]) -> bool:
    """
    draft -> requester_submitted

    Requires:
    - draft status
    - requester signature present
    - declared impact block present
    """
    if entry.get("decision_status") != "draft":
        return False

    requester = entry.get("requested_by", {})
    declared_impact = entry.get("declared_impact", {})
    return bool(requester.get("signature")) and isinstance(declared_impact, dict)


def can_enter_approver_review(entry: Dict[str, Any]) -> bool:
    """
    requester_submitted -> approver_review

    Requires:
    - requester_submitted status
    - approver identity recorded (signature not required yet)
    """
    if entry.get("decision_status") != "requester_submitted":
        return False

    approved_by = entry.get("approved_by", {})
    return bool(approved_by.get("name")) and bool(approved_by.get("role"))


def can_approve_decision(entry: Dict[str, Any]) -> bool:
    """
    approver_review -> approved

    Requires:
    - approver_review status
    - approver signature
    - if expected_cost_delta_amount > 0 then linked_change_packet_id must be present
    - if expected_schedule_delta_days != 0 then phase_id must be present
    """
    if entry.get("decision_status") != "approver_review":
        return False

    approved_by = entry.get("approved_by", {})
    if not approved_by.get("signature"):
        return False

    declared_impact = entry.get("declared_impact", {})
    context_lock = entry.get("context_lock", {})

    expected_cost_delta_amount = declared_impact.get("expected_cost_delta_amount")
    expected_schedule_delta_days = declared_impact.get("expected_schedule_delta_days")

    if expected_cost_delta_amount is not None and float(expected_cost_delta_amount) > 0:
        if not context_lock.get("linked_change_packet_id"):
            return False

    if expected_schedule_delta_days is not None and float(expected_schedule_delta_days) != 0:
        if not context_lock.get("phase_id"):
            return False

    return True


def can_reject_decision(entry: Dict[str, Any]) -> bool:
    """
    approver_review -> rejected

    Requires:
    - approver_review status
    - approver signature
    """
    if entry.get("decision_status") != "approver_review":
        return False

    approved_by = entry.get("approved_by", {})
    return bool(approved_by.get("signature"))
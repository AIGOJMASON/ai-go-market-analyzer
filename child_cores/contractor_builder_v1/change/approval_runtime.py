"""
Approval runtime for contractor_builder_v1 changes.

This module enforces simple lawful status and signature rules for change packets.
It does not auto-approve. It only checks readiness and applies signatures.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def apply_requester_signature(
    packet: Dict[str, Any],
    *,
    name: str,
    signature: str,
) -> Dict[str, Any]:
    updated = dict(packet)
    signatures = dict(updated.get("signatures", {}))
    requester = dict(signatures.get("requester", {}))
    requester.update(
        {
            "name": name,
            "signature": signature,
            "timestamp": _utc_now_iso(),
        }
    )
    signatures["requester"] = requester
    updated["signatures"] = signatures
    return updated


def apply_approver_signature(
    packet: Dict[str, Any],
    *,
    name: str,
    signature: str,
) -> Dict[str, Any]:
    updated = dict(packet)
    signatures = dict(updated.get("signatures", {}))
    approver = dict(signatures.get("approver", {}))
    approver.update(
        {
            "name": name,
            "signature": signature,
            "timestamp": _utc_now_iso(),
        }
    )
    signatures["approver"] = approver
    updated["signatures"] = signatures
    return updated


def apply_pm_signature(
    packet: Dict[str, Any],
    *,
    name: str,
    signature: str,
) -> Dict[str, Any]:
    updated = dict(packet)
    signatures = dict(updated.get("signatures", {}))
    pm = dict(signatures.get("pm", {}))
    pm.update(
        {
            "name": name,
            "signature": signature,
            "timestamp": _utc_now_iso(),
        }
    )
    signatures["pm"] = pm
    updated["signatures"] = signatures
    return updated


def can_submit_change_packet(packet: Dict[str, Any]) -> bool:
    """
    Draft -> requester_submitted

    Requires:
    - draft status
    - requester signature
    """
    if packet.get("status") != "draft":
        return False

    requester = packet.get("signatures", {}).get("requester", {})
    return bool(requester.get("signature"))


def can_move_to_pending_approvals(packet: Dict[str, Any]) -> bool:
    """
    priced -> pending_approvals

    Requires:
    - priced status
    - total change amount present
    - total schedule delta present
    """
    if packet.get("status") != "priced":
        return False

    cost_total = (
        packet.get("deterministic_block", {})
        .get("cost_delta", {})
        .get("total_change_order_amount")
    )
    schedule_total = (
        packet.get("deterministic_block", {})
        .get("time_delta", {})
        .get("total_schedule_delta_days")
    )
    return cost_total is not None and schedule_total is not None


def can_approve_change_packet(packet: Dict[str, Any]) -> bool:
    """
    pending_approvals -> approved

    Requires:
    - pending_approvals status
    - requester signature
    - approver signature
    - PM signature
    """
    if packet.get("status") != "pending_approvals":
        return False

    signatures = packet.get("signatures", {})
    requester_ok = bool(signatures.get("requester", {}).get("signature"))
    approver_ok = bool(signatures.get("approver", {}).get("signature"))
    pm_ok = bool(signatures.get("pm", {}).get("signature"))
    return requester_ok and approver_ok and pm_ok
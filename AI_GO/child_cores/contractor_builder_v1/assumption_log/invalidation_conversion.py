"""
Invalidation conversion helpers for contractor_builder_v1 assumptions.

This module enforces the doctrine that invalidated assumptions require an explicit
downstream conversion decision rather than silent status change.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict

INVALIDATION_CONVERSION_OPTIONS = [
    "Create_Decision",
    "Create_Change_Packet",
    "Link_to_Risk",
    "Declare_No_Impact",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def validate_invalidation_conversion_option(option: str) -> bool:
    """
    Return True if the conversion option is canonical.
    """
    return option in INVALIDATION_CONVERSION_OPTIONS


def build_invalidation_conversion_record(
    *,
    project_id: str,
    assumption_id: str,
    conversion_option: str,
    actor_name: str,
    actor_role: str,
    linked_decision_id: str = "",
    linked_change_packet_id: str = "",
    linked_risk_id: str = "",
    rationale: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical invalidation conversion record.
    """
    if not validate_invalidation_conversion_option(conversion_option):
        raise ValueError(
            f"conversion_option must be one of {INVALIDATION_CONVERSION_OPTIONS}"
        )

    return {
        "generated_at": _utc_now_iso(),
        "project_id": project_id,
        "assumption_id": assumption_id,
        "conversion_option": conversion_option,
        "actor_name": actor_name,
        "actor_role": actor_role,
        "linked_decision_id": linked_decision_id or None,
        "linked_change_packet_id": linked_change_packet_id or None,
        "linked_risk_id": linked_risk_id or None,
        "rationale": rationale,
    }
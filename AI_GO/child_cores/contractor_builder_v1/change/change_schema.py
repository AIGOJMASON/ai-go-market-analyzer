"""
Change packet schema for contractor_builder_v1.

This module defines the canonical change packet contract for phase amendments,
rebids, remodel pricing, dead-time costing, schedule delta logic, approval flow,
and Stage 5 customer-impact/signoff governance.

It defines structure only.
It does NOT:
- price changes
- send communication
- approve changes
- mutate workflow truth
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from ..governance.shared_enums import SHARED_ENUMS

CHANGE_SCHEMA_VERSION = "v2"

_ALLOWED_REMODEL_PHASE_STATUS = {
    "not_started",
    "in_progress",
    "adjacent_complete",
    "closed_signed_off",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _empty_cost_delta_block() -> Dict[str, Any]:
    return {
        "material_delta_amount": None,
        "labor_delta_direct_amount": None,
        "labor_inefficiency_multiplier": None,
        "dead_time_hours_estimate": None,
        "dead_time_cost_estimate": None,
        "supervision_delta_amount": None,
        "general_conditions_delta_amount": None,
        "total_change_order_amount": None,
    }


def _empty_time_delta_block() -> Dict[str, Any]:
    return {
        "base_time_delta_days": None,
        "dead_time_days_estimate": None,
        "inspection_reset_days_estimate": None,
        "resequencing_days_estimate": None,
        "total_schedule_delta_days": None,
        "cascade_risk_label": "",
    }


def _empty_customer_impact_block() -> Dict[str, Any]:
    return {
        "requires_customer_signoff": None,
        "impact_reason": "",
        "customer_visible_summary": "",
        "blocks_phase_closeout_when_unresolved": None,
    }


def _empty_change_signoff_block() -> Dict[str, Any]:
    return {
        "status": "not_requested",
        "latest_delivery_id": "",
        "latest_delivery_status": "",
        "sent_at": None,
        "signed_at": None,
        "declined_at": None,
    }


def build_change_packet(
    *,
    change_packet_id: str,
    project_id: str,
    phase_id: str,
    title: str,
    originator_name: str,
    originator_role: str,
    originator_org: str,
    workflow_phase_state_snapshot_id: str,
    compliance_snapshot_id: str,
    drawing_revision_id: str,
    budget_baseline_id: str,
    schedule_baseline_id: str,
    scope_delta_description: str,
    added_items: Optional[List[str]] = None,
    removed_items: Optional[List[str]] = None,
    scope_notes: str = "",
    phase_status: str = "",
    disruption_multiplier: Optional[float] = None,
    factors_applied: Optional[List[str]] = None,
    customer_visible_summary: str = "",
    impact_reason: str = "",
    requires_customer_signoff: Optional[bool] = None,
    blocks_phase_closeout_when_unresolved: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Build a canonical draft change packet.
    """
    if phase_status and phase_status not in _ALLOWED_REMODEL_PHASE_STATUS:
        raise ValueError(
            "phase_status must be one of: "
            + ", ".join(sorted(_ALLOWED_REMODEL_PHASE_STATUS))
        )

    packet: Dict[str, Any] = {
        "schema_version": CHANGE_SCHEMA_VERSION,
        "change_packet_id": change_packet_id,
        "project_id": project_id,
        "phase_id": phase_id,
        "title": title,
        "originator": {
            "name": originator_name,
            "role": originator_role,
            "org": originator_org,
        },
        "status": "draft",
        "requested_at": _utc_now_iso(),
        "approved_at": None,
        "context_lock": {
            "workflow_phase_state_snapshot_id": workflow_phase_state_snapshot_id,
            "compliance_snapshot_id": compliance_snapshot_id,
            "drawing_revision_id": drawing_revision_id,
            "budget_baseline_id": budget_baseline_id,
            "schedule_baseline_id": schedule_baseline_id,
        },
        "scope_delta": {
            "description": scope_delta_description,
            "added_items": list(added_items or []),
            "removed_items": list(removed_items or []),
            "notes": scope_notes,
        },
        "deterministic_block": {
            "cost_delta": _empty_cost_delta_block(),
            "time_delta": _empty_time_delta_block(),
            "remodel_context_applied": {
                "phase_status": phase_status,
                "disruption_multiplier": disruption_multiplier,
                "factors_applied": list(factors_applied or []),
            },
        },
        "customer_impact": {
            "requires_customer_signoff": requires_customer_signoff,
            "impact_reason": impact_reason,
            "customer_visible_summary": customer_visible_summary,
            "blocks_phase_closeout_when_unresolved": blocks_phase_closeout_when_unresolved,
        },
        "change_signoff": _empty_change_signoff_block(),
        "human_interface_layer": {
            "auto_summary_draft": "",
            "pm_notes": "",
        },
        "signatures": {
            "requester": {
                "name": "",
                "signature": None,
                "timestamp": None,
            },
            "approver": {
                "name": "",
                "signature": None,
                "timestamp": None,
            },
            "pm": {
                "name": "",
                "signature": None,
                "timestamp": None,
            },
        },
        "integrity": {
            "packet_hash": "",
            "linked_receipts": [],
            "supersedes_change_packet_id": None,
        },
        "allowed_statuses": list(SHARED_ENUMS["change_packet_status"]),
    }
    return packet


def validate_change_packet(packet: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a change packet.
    """
    errors: List[str] = []

    required_fields = [
        "change_packet_id",
        "project_id",
        "phase_id",
        "title",
        "originator",
        "status",
        "requested_at",
        "context_lock",
        "scope_delta",
        "deterministic_block",
        "customer_impact",
        "change_signoff",
        "human_interface_layer",
        "signatures",
        "integrity",
    ]
    for field in required_fields:
        if field not in packet:
            errors.append(f"Missing required change packet field: {field}")

    if not packet.get("change_packet_id"):
        errors.append("change_packet_id may not be empty")
    if not packet.get("project_id"):
        errors.append("project_id may not be empty")
    if not packet.get("phase_id"):
        errors.append("phase_id may not be empty")
    if not packet.get("title"):
        errors.append("title may not be empty")

    status = packet.get("status")
    if status not in SHARED_ENUMS["change_packet_status"]:
        errors.append(
            f"status must be one of {SHARED_ENUMS['change_packet_status']}"
        )

    context_lock = packet.get("context_lock", {})
    if not isinstance(context_lock, dict):
        errors.append("context_lock must be a mapping")
    else:
        required_context_fields = [
            "workflow_phase_state_snapshot_id",
            "compliance_snapshot_id",
            "drawing_revision_id",
            "budget_baseline_id",
            "schedule_baseline_id",
        ]
        for field in required_context_fields:
            if not context_lock.get(field):
                errors.append(f"Missing context_lock field: {field}")

    scope_delta = packet.get("scope_delta", {})
    if not isinstance(scope_delta, dict):
        errors.append("scope_delta must be a mapping")
    else:
        if not scope_delta.get("description"):
            errors.append("scope_delta.description may not be empty")

    deterministic_block = packet.get("deterministic_block", {})
    if not isinstance(deterministic_block, dict):
        errors.append("deterministic_block must be a mapping")
    else:
        if not isinstance(deterministic_block.get("cost_delta", {}), dict):
            errors.append("deterministic_block.cost_delta must be a mapping")
        if not isinstance(deterministic_block.get("time_delta", {}), dict):
            errors.append("deterministic_block.time_delta must be a mapping")
        remodel_context = deterministic_block.get("remodel_context_applied", {})
        if not isinstance(remodel_context, dict):
            errors.append("deterministic_block.remodel_context_applied must be a mapping")
        else:
            phase_status = str(remodel_context.get("phase_status", "")).strip()
            if phase_status and phase_status not in _ALLOWED_REMODEL_PHASE_STATUS:
                errors.append(
                    "remodel_context_applied.phase_status must be one of: "
                    + ", ".join(sorted(_ALLOWED_REMODEL_PHASE_STATUS))
                )

    customer_impact = packet.get("customer_impact", {})
    if not isinstance(customer_impact, dict):
        errors.append("customer_impact must be a mapping")
    else:
        for boolean_field in [
            "requires_customer_signoff",
            "blocks_phase_closeout_when_unresolved",
        ]:
            value = customer_impact.get(boolean_field)
            if value is not None and not isinstance(value, bool):
                errors.append(f"customer_impact.{boolean_field} must be boolean or null")

    change_signoff = packet.get("change_signoff", {})
    if not isinstance(change_signoff, dict):
        errors.append("change_signoff must be a mapping")
    else:
        signoff_status = str(change_signoff.get("status", "")).strip()
        allowed_signoff_statuses = {"not_requested", "sent", "signed", "declined"}
        if signoff_status and signoff_status not in allowed_signoff_statuses:
            errors.append(
                "change_signoff.status must be one of "
                + str(sorted(allowed_signoff_statuses))
            )

    return errors


def get_change_packet_template() -> Dict[str, Any]:
    """
    Return an empty change packet template.
    """
    return deepcopy(
        {
            "schema_version": CHANGE_SCHEMA_VERSION,
            "change_packet_id": "",
            "project_id": "",
            "phase_id": "",
            "title": "",
            "originator": {
                "name": "",
                "role": "",
                "org": "",
            },
            "status": "draft",
            "requested_at": "",
            "approved_at": None,
            "context_lock": {
                "workflow_phase_state_snapshot_id": "",
                "compliance_snapshot_id": "",
                "drawing_revision_id": "",
                "budget_baseline_id": "",
                "schedule_baseline_id": "",
            },
            "scope_delta": {
                "description": "",
                "added_items": [],
                "removed_items": [],
                "notes": "",
            },
            "deterministic_block": {
                "cost_delta": _empty_cost_delta_block(),
                "time_delta": _empty_time_delta_block(),
                "remodel_context_applied": {
                    "phase_status": "",
                    "disruption_multiplier": None,
                    "factors_applied": [],
                },
            },
            "customer_impact": _empty_customer_impact_block(),
            "change_signoff": _empty_change_signoff_block(),
            "human_interface_layer": {
                "auto_summary_draft": "",
                "pm_notes": "",
            },
            "signatures": {
                "requester": {
                    "name": "",
                    "signature": None,
                    "timestamp": None,
                },
                "approver": {
                    "name": "",
                    "signature": None,
                    "timestamp": None,
                },
                "pm": {
                    "name": "",
                    "signature": None,
                    "timestamp": None,
                },
            },
            "integrity": {
                "packet_hash": "",
                "linked_receipts": [],
                "supersedes_change_packet_id": None,
            },
            "allowed_statuses": list(SHARED_ENUMS["change_packet_status"]),
        }
    )
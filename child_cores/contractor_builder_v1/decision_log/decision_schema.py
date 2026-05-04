"""
Decision schema for contractor_builder_v1.

This module defines the canonical internal-only decision governance record used for:
- context-locked internal decisions
- declared impact tracking
- dual acknowledgment flow
- append-only revision posture
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from ..governance.shared_enums import SHARED_ENUMS

DECISION_SCHEMA_VERSION = "v1"

DECISION_TYPE_ENUM = [
    "Scope_Clarification",
    "Design_Adjustment",
    "Cost_Acceptance",
    "Schedule_Adjustment",
    "Risk_Acceptance",
    "Vendor_Selection",
    "Compliance_Clarification",
    "Sequence_Change",
    "Quality_Standard_Change",
    "Client_Request_Confirmation",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_decision_entry(
    *,
    decision_id: str,
    project_id: str,
    title: str,
    decision_type: str,
    phase_id: str = "",
    linked_change_packet_id: str = "",
    compliance_snapshot_id: str = "",
    schedule_baseline_id: str = "",
    budget_baseline_id: str = "",
    drawing_revision_id: str = "",
    oracle_snapshot_id: str = "",
    expected_schedule_delta_days: Optional[float] = None,
    expected_cost_delta_amount: Optional[float] = None,
    expected_margin_delta_percent: Optional[float] = None,
    expected_risk_level: str = "",
    notes_on_assumptions: str = "",
    may_reference_in_owner_reports: bool = True,
    owner_report_reference_label: str = "",
    notes_internal: str = "",
    attachments_refs: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Build a canonical draft decision entry.
    """
    if decision_type not in DECISION_TYPE_ENUM:
        raise ValueError(f"decision_type must be one of {DECISION_TYPE_ENUM}")

    if expected_risk_level and expected_risk_level not in SHARED_ENUMS["impact_level"]:
        raise ValueError(
            f"expected_risk_level must be one of {SHARED_ENUMS['impact_level']}"
        )

    return {
        "schema_version": DECISION_SCHEMA_VERSION,
        "decision_id": decision_id,
        "project_id": project_id,
        "title": title,
        "decision_type": decision_type,
        "decision_status": "draft",
        "requested_by": {
            "name": "",
            "role": "",
            "org": "",
            "signature": None,
            "timestamp": None,
        },
        "approved_by": {
            "name": "",
            "role": "",
            "org": "",
            "signature": None,
            "timestamp": None,
        },
        "dates": {
            "created_at": _utc_now_iso(),
            "requested_at": _utc_now_iso(),
            "submitted_at": None,
            "approved_at": None,
            "rejected_at": None,
        },
        "context_lock": {
            "phase_id": phase_id or None,
            "linked_change_packet_id": linked_change_packet_id or None,
            "compliance_snapshot_id": compliance_snapshot_id or None,
            "schedule_baseline_id": schedule_baseline_id or None,
            "budget_baseline_id": budget_baseline_id or None,
            "drawing_revision_id": drawing_revision_id or None,
            "oracle_snapshot_id": oracle_snapshot_id or None,
        },
        "declared_impact": {
            "expected_schedule_delta_days": expected_schedule_delta_days,
            "expected_cost_delta_amount": expected_cost_delta_amount,
            "expected_margin_delta_percent": expected_margin_delta_percent,
            "expected_risk_level": expected_risk_level,
            "notes_on_assumptions": notes_on_assumptions,
        },
        "attachments_refs": list(attachments_refs or []),
        "notes_internal": notes_internal,
        "reporting_refs": {
            "may_reference_in_owner_reports": may_reference_in_owner_reports,
            "owner_report_reference_label": owner_report_reference_label,
        },
        "integrity": {
            "entry_hash": "",
            "linked_receipts": [],
            "supersedes_decision_id": None,
        },
        "allowed_decision_types": DECISION_TYPE_ENUM,
        "allowed_statuses": SHARED_ENUMS["decision_status"],
    }


def validate_decision_entry(entry: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a decision entry.
    """
    errors: List[str] = []

    required_fields = [
        "decision_id",
        "project_id",
        "title",
        "decision_type",
        "decision_status",
        "requested_by",
        "approved_by",
        "dates",
        "context_lock",
        "declared_impact",
        "attachments_refs",
        "notes_internal",
        "reporting_refs",
        "integrity",
    ]
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required decision field: {field}")

    if not entry.get("decision_id"):
        errors.append("decision_id may not be empty")
    if not entry.get("project_id"):
        errors.append("project_id may not be empty")
    if not entry.get("title"):
        errors.append("title may not be empty")

    decision_type = entry.get("decision_type")
    if decision_type not in DECISION_TYPE_ENUM:
        errors.append(f"decision_type must be one of {DECISION_TYPE_ENUM}")

    status = entry.get("decision_status")
    if status not in SHARED_ENUMS["decision_status"]:
        errors.append(
            f"decision_status must be one of {SHARED_ENUMS['decision_status']}"
        )

    context_lock = entry.get("context_lock", {})
    if not isinstance(context_lock, dict):
        errors.append("context_lock must be a mapping")

    declared_impact = entry.get("declared_impact", {})
    if not isinstance(declared_impact, dict):
        errors.append("declared_impact must be a mapping")
    else:
        risk_level = declared_impact.get("expected_risk_level", "")
        if risk_level and risk_level not in SHARED_ENUMS["impact_level"]:
            errors.append(
                f"declared_impact.expected_risk_level must be one of "
                f"{SHARED_ENUMS['impact_level']}"
            )

    return errors


def get_decision_entry_template() -> Dict[str, Any]:
    """
    Return an empty decision entry template.
    """
    return deepcopy(
        {
            "schema_version": DECISION_SCHEMA_VERSION,
            "decision_id": "",
            "project_id": "",
            "title": "",
            "decision_type": "",
            "decision_status": "draft",
            "requested_by": {
                "name": "",
                "role": "",
                "org": "",
                "signature": None,
                "timestamp": None,
            },
            "approved_by": {
                "name": "",
                "role": "",
                "org": "",
                "signature": None,
                "timestamp": None,
            },
            "dates": {
                "created_at": "",
                "requested_at": "",
                "submitted_at": None,
                "approved_at": None,
                "rejected_at": None,
            },
            "context_lock": {
                "phase_id": None,
                "linked_change_packet_id": None,
                "compliance_snapshot_id": None,
                "schedule_baseline_id": None,
                "budget_baseline_id": None,
                "drawing_revision_id": None,
                "oracle_snapshot_id": None,
            },
            "declared_impact": {
                "expected_schedule_delta_days": None,
                "expected_cost_delta_amount": None,
                "expected_margin_delta_percent": None,
                "expected_risk_level": "",
                "notes_on_assumptions": "",
            },
            "attachments_refs": [],
            "notes_internal": "",
            "reporting_refs": {
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": "",
            },
            "integrity": {
                "entry_hash": "",
                "linked_receipts": [],
                "supersedes_decision_id": None,
            },
            "allowed_decision_types": DECISION_TYPE_ENUM,
            "allowed_statuses": SHARED_ENUMS["decision_status"],
        }
    )
"""
Router schema for contractor_builder_v1.

This module defines the canonical advisory records used for:
- schedule blocks
- conflict reports
- capacity posture
- cascade risk summaries

Router outputs are advisory only. They do not mutate workflow, crews, or project truth.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

ROUTER_SCHEMA_VERSION = "v1"

BLOCK_TYPE_ENUM = [
    "Crew_Assignment",
    "Subcontractor_Window",
    "Inspection_Window",
    "Material_Delivery",
    "Access_Restriction",
    "Utility_Shutdown",
    "Weather_Hold",
    "Owner_Access",
    "Other",
]

CONFLICT_TYPE_ENUM = [
    "Date_Overlap",
    "Dependency_Violation",
    "Trade_Overlap",
    "Access_Collision",
    "Inspection_Blocked",
    "Material_Timing_Mismatch",
    "Crew_Double_Booked",
    "Other",
]

CAPACITY_STATUS_ENUM = [
    "Healthy",
    "Watch",
    "Overloaded",
]

CASCADE_RISK_ENUM = [
    "none",
    "low",
    "moderate",
    "high",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_schedule_block(
    *,
    block_id: str,
    project_id: str,
    phase_id: str,
    block_type: str,
    start_date: str,
    end_date: str,
    resource_name: str = "",
    resource_type: str = "",
    dependency_phase_ids: Optional[List[str]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical schedule block record.
    """
    if block_type not in BLOCK_TYPE_ENUM:
        raise ValueError(f"block_type must be one of {BLOCK_TYPE_ENUM}")

    return {
        "schema_version": ROUTER_SCHEMA_VERSION,
        "block_id": block_id,
        "project_id": project_id,
        "phase_id": phase_id,
        "block_type": block_type,
        "start_date": start_date,
        "end_date": end_date,
        "resource_name": resource_name,
        "resource_type": resource_type,
        "dependency_phase_ids": list(dependency_phase_ids or []),
        "notes": notes,
        "created_at": _utc_now_iso(),
        "allowed_block_types": BLOCK_TYPE_ENUM,
    }


def validate_schedule_block(block: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a schedule block.
    """
    errors: List[str] = []

    required_fields = [
        "block_id",
        "project_id",
        "phase_id",
        "block_type",
        "start_date",
        "end_date",
    ]
    for field in required_fields:
        if field not in block:
            errors.append(f"Missing required schedule block field: {field}")

    if not block.get("block_id"):
        errors.append("block_id may not be empty")
    if not block.get("project_id"):
        errors.append("project_id may not be empty")
    if not block.get("phase_id"):
        errors.append("phase_id may not be empty")
    if not block.get("start_date"):
        errors.append("start_date may not be empty")
    if not block.get("end_date"):
        errors.append("end_date may not be empty")

    block_type = block.get("block_type")
    if block_type not in BLOCK_TYPE_ENUM:
        errors.append(f"block_type must be one of {BLOCK_TYPE_ENUM}")

    return errors


def build_conflict_record(
    *,
    project_id: str,
    conflict_id: str,
    conflict_type: str,
    primary_block_id: str,
    secondary_block_id: str,
    primary_phase_id: str,
    secondary_phase_id: str,
    severity: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical conflict record.
    """
    if conflict_type not in CONFLICT_TYPE_ENUM:
        raise ValueError(f"conflict_type must be one of {CONFLICT_TYPE_ENUM}")

    return {
        "schema_version": ROUTER_SCHEMA_VERSION,
        "generated_at": _utc_now_iso(),
        "project_id": project_id,
        "conflict_id": conflict_id,
        "conflict_type": conflict_type,
        "primary_block_id": primary_block_id,
        "secondary_block_id": secondary_block_id,
        "primary_phase_id": primary_phase_id,
        "secondary_phase_id": secondary_phase_id,
        "severity": severity,
        "notes": notes,
        "allowed_conflict_types": CONFLICT_TYPE_ENUM,
    }


def build_capacity_record(
    *,
    project_id: str,
    snapshot_id: str,
    resource_name: str,
    resource_type: str,
    assigned_block_count: int,
    concurrent_block_count: int,
    capacity_limit: int,
    capacity_status: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical capacity posture record.
    """
    if capacity_status not in CAPACITY_STATUS_ENUM:
        raise ValueError(
            f"capacity_status must be one of {CAPACITY_STATUS_ENUM}"
        )

    return {
        "schema_version": ROUTER_SCHEMA_VERSION,
        "generated_at": _utc_now_iso(),
        "project_id": project_id,
        "snapshot_id": snapshot_id,
        "resource_name": resource_name,
        "resource_type": resource_type,
        "assigned_block_count": assigned_block_count,
        "concurrent_block_count": concurrent_block_count,
        "capacity_limit": capacity_limit,
        "capacity_status": capacity_status,
        "notes": notes,
        "allowed_capacity_statuses": CAPACITY_STATUS_ENUM,
    }


def build_cascade_risk_record(
    *,
    project_id: str,
    report_id: str,
    cascade_risk_label: str,
    conflict_count: int,
    dependency_violation_count: int,
    overloaded_resource_count: int,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical cascade risk advisory record.
    """
    if cascade_risk_label not in CASCADE_RISK_ENUM:
        raise ValueError(
            f"cascade_risk_label must be one of {CASCADE_RISK_ENUM}"
        )

    return {
        "schema_version": ROUTER_SCHEMA_VERSION,
        "generated_at": _utc_now_iso(),
        "project_id": project_id,
        "report_id": report_id,
        "cascade_risk_label": cascade_risk_label,
        "conflict_count": conflict_count,
        "dependency_violation_count": dependency_violation_count,
        "overloaded_resource_count": overloaded_resource_count,
        "notes": notes,
        "allowed_cascade_risk": CASCADE_RISK_ENUM,
    }


def get_schedule_block_template() -> Dict[str, Any]:
    """
    Return an empty schedule block template.
    """
    return deepcopy(
        {
            "schema_version": ROUTER_SCHEMA_VERSION,
            "block_id": "",
            "project_id": "",
            "phase_id": "",
            "block_type": "",
            "start_date": "",
            "end_date": "",
            "resource_name": "",
            "resource_type": "",
            "dependency_phase_ids": [],
            "notes": "",
            "created_at": "",
            "allowed_block_types": BLOCK_TYPE_ENUM,
        }
    )
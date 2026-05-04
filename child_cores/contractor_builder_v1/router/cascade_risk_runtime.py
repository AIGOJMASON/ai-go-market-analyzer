"""
Cascade risk runtime for contractor_builder_v1.

This module translates conflict and capacity pressure into a simple advisory
cascade risk label. It does not mutate schedules or generate changes.
"""

from __future__ import annotations

from typing import Dict, List

from .router_schema import build_cascade_risk_record


def classify_cascade_risk(
    *,
    conflict_count: int,
    dependency_violation_count: int,
    overloaded_resource_count: int,
) -> str:
    """
    Classify advisory cascade risk from routing pressure signals.
    """
    pressure_score = (
        conflict_count
        + (dependency_violation_count * 2)
        + (overloaded_resource_count * 2)
    )

    if pressure_score <= 0:
        return "none"
    if pressure_score <= 2:
        return "low"
    if pressure_score <= 5:
        return "moderate"
    return "high"


def build_cascade_risk_from_conflicts(
    *,
    project_id: str,
    report_id: str,
    conflicts: List[Dict[str, object]],
    capacity_records: List[Dict[str, object]],
    notes: str = "",
) -> Dict[str, object]:
    """
    Build a cascade risk record from conflict and capacity posture inputs.
    """
    dependency_violation_count = sum(
        1 for conflict in conflicts
        if conflict.get("conflict_type") == "Dependency_Violation"
    )
    overloaded_resource_count = sum(
        1 for record in capacity_records
        if record.get("capacity_status") == "Overloaded"
    )
    conflict_count = len(conflicts)

    cascade_risk_label = classify_cascade_risk(
        conflict_count=conflict_count,
        dependency_violation_count=dependency_violation_count,
        overloaded_resource_count=overloaded_resource_count,
    )

    return build_cascade_risk_record(
        project_id=project_id,
        report_id=report_id,
        cascade_risk_label=cascade_risk_label,
        conflict_count=conflict_count,
        dependency_violation_count=dependency_violation_count,
        overloaded_resource_count=overloaded_resource_count,
        notes=notes,
    )
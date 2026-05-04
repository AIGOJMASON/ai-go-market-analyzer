"""
Workflow to change adapter for contractor_builder_v1.

This adapter extracts the minimum lawful workflow context required to create
or validate a change packet. It performs translation only and does not price,
approve, or mutate any change records.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _find_phase_instance(
    *,
    phase_instances: List[Dict[str, Any]],
    phase_id: str,
) -> Dict[str, Any]:
    for instance in phase_instances:
        if str(instance.get("phase_id", "")) == phase_id:
            return dict(instance)
    raise KeyError(f"Unknown phase_id in workflow_to_change_adapter: {phase_id}")


def build_change_context_from_workflow(
    *,
    project_id: str,
    phase_id: str,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
    workflow_phase_state_snapshot_id: str,
    schedule_baseline_id: str,
) -> Dict[str, Any]:
    """
    Build the minimum workflow-derived context block for the change branch.
    """
    phase_instance = _find_phase_instance(
        phase_instances=phase_instances,
        phase_id=phase_id,
    )

    return {
        "project_id": project_id,
        "phase_id": phase_id,
        "workflow_phase_state_snapshot_id": workflow_phase_state_snapshot_id,
        "workflow_status": workflow_state.get("workflow_status", ""),
        "current_phase_id": workflow_state.get("current_phase_id", ""),
        "phase_name": phase_instance.get("phase_name", ""),
        "phase_status": phase_instance.get("phase_status", ""),
        "planned_start_date": phase_instance.get("planned_start_date", ""),
        "planned_end_date": phase_instance.get("planned_end_date", ""),
        "actual_start_date": phase_instance.get("actual_start_date", ""),
        "actual_end_date": phase_instance.get("actual_end_date", ""),
        "expected_duration_days": phase_instance.get("expected_duration_days"),
        "actual_duration_days": phase_instance.get("actual_duration_days"),
        "dependency_phase_ids": list(phase_instance.get("dependencies", [])),
        "schedule_baseline_id": schedule_baseline_id,
    }
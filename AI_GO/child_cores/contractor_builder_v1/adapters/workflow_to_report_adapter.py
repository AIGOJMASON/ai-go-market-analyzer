"""
Workflow to report adapter for contractor_builder_v1.

This adapter produces the bounded workflow snapshot used by the report branch.
It performs thin field shaping only.

It owns:
- workflow snapshot shaping for reporting
- bounded phase-state summaries

It does NOT:
- mutate workflow state
- infer missing approvals
- compute readiness
- decide which phase should advance
"""

from __future__ import annotations

from typing import Any, Dict, List


def _normalize_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_phase_instances(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _phase_status(instance: Dict[str, Any]) -> str:
    return str(instance.get("phase_status", "")).strip()


def _phase_name(instance: Dict[str, Any]) -> str:
    return str(instance.get("phase_name", "")).strip()


def _phase_id(instance: Dict[str, Any]) -> str:
    return str(instance.get("phase_id", "")).strip()


def build_workflow_report_snapshot(
    *,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded workflow snapshot for reporting.

    Reporting posture:
    - numbers and explicit state first
    - no new workflow truth invented here
    - only already-structured phase status is summarized
    """
    workflow_state_clean = _normalize_mapping(workflow_state)
    phase_instances_clean = _normalize_phase_instances(phase_instances)

    active_phase_names = [
        _phase_name(instance)
        for instance in phase_instances_clean
        if _phase_status(instance) == "in_progress" and _phase_name(instance)
    ]

    blocked_phase_ids = [
        _phase_id(instance)
        for instance in phase_instances_clean
        if _phase_status(instance) == "blocked" and _phase_id(instance)
    ]

    awaiting_signoff_phase_ids = [
        _phase_id(instance)
        for instance in phase_instances_clean
        if _phase_status(instance) == "awaiting_signoff" and _phase_id(instance)
    ]

    complete_phase_ids = [
        _phase_id(instance)
        for instance in phase_instances_clean
        if _phase_status(instance) == "complete" and _phase_id(instance)
    ]

    closed_phase_ids = [
        _phase_id(instance)
        for instance in phase_instances_clean
        if _phase_status(instance) == "closed" and _phase_id(instance)
    ]

    return {
        "workflow_status": str(workflow_state_clean.get("workflow_status", "")).strip(),
        "phase_count": int(workflow_state_clean.get("phase_count", len(phase_instances_clean))),
        "current_phase_id": str(workflow_state_clean.get("current_phase_id", "")).strip(),
        "active_phase_names": active_phase_names,
        "blocked_phase_ids": blocked_phase_ids,
        "awaiting_signoff_phase_ids": awaiting_signoff_phase_ids,
        "complete_phase_ids": complete_phase_ids,
        "closed_phase_ids": closed_phase_ids,
    }
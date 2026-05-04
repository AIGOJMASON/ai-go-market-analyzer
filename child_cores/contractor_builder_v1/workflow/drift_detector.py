"""
Drift detector for contractor_builder_v1 workflow.

This module compares expected vs actual phase timing and creates advisory drift records.
It does not mutate schedules. It only reports deviations and dead-time risk estimates.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _derive_dead_time_risk_label(schedule_drift_days: int) -> str:
    """
    Map schedule drift to a simple advisory dead-time risk label.
    """
    if schedule_drift_days <= 0:
        return "none"
    if schedule_drift_days <= 2:
        return "low"
    if schedule_drift_days <= 5:
        return "moderate"
    return "high"


def build_phase_drift_record(
    *,
    project_id: str,
    phase_id: str,
    expected_duration_days: int,
    actual_duration_days: Optional[int],
    dead_time_hours_estimate: float = 0.0,
) -> Dict[str, Any]:
    """
    Build a canonical phase drift record.
    """
    actual_days = actual_duration_days if actual_duration_days is not None else 0
    schedule_drift_days = actual_days - expected_duration_days
    dead_time_risk_label = _derive_dead_time_risk_label(schedule_drift_days)

    return {
        "project_id": project_id,
        "phase_id": phase_id,
        "generated_at": _utc_now_iso(),
        "expected_duration_days": expected_duration_days,
        "actual_duration_days": actual_duration_days,
        "schedule_drift_days": schedule_drift_days,
        "dead_time_hours_estimate": dead_time_hours_estimate,
        "dead_time_risk_label": dead_time_risk_label,
    }


def detect_phase_drift(phase_instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce a drift record from a phase instance.
    """
    return build_phase_drift_record(
        project_id=phase_instance["project_id"],
        phase_id=phase_instance["phase_id"],
        expected_duration_days=phase_instance["expected_duration_days"],
        actual_duration_days=phase_instance.get("actual_duration_days"),
        dead_time_hours_estimate=float(
            phase_instance.get("drift", {}).get("dead_time_hours_estimate", 0.0)
        ),
    )
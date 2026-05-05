"""
Schedule delta model for contractor_builder_v1 changes.

This module computes the deterministic time-delta block for a change packet,
including base time, dead time, inspection reset days, resequencing days,
and a cascade risk label.
"""

from __future__ import annotations

from typing import Dict, Optional


def _safe_days(value: Optional[float]) -> float:
    if value is None:
        return 0.0
    return float(value)


def _derive_cascade_risk_label(total_schedule_delta_days: float) -> str:
    """
    Convert total schedule delta into a simple advisory cascade risk label.
    """
    if total_schedule_delta_days <= 0:
        return "none"
    if total_schedule_delta_days <= 2:
        return "low"
    if total_schedule_delta_days <= 5:
        return "moderate"
    return "high"


def compute_total_schedule_delta_days(
    *,
    base_time_delta_days: Optional[float],
    dead_time_days_estimate: Optional[float],
    inspection_reset_days_estimate: Optional[float],
    resequencing_days_estimate: Optional[float],
) -> float:
    """
    Compute total schedule delta in days.
    """
    total = (
        _safe_days(base_time_delta_days)
        + _safe_days(dead_time_days_estimate)
        + _safe_days(inspection_reset_days_estimate)
        + _safe_days(resequencing_days_estimate)
    )
    return round(total, 2)


def build_time_delta_block(
    *,
    base_time_delta_days: Optional[float],
    dead_time_days_estimate: Optional[float],
    inspection_reset_days_estimate: Optional[float],
    resequencing_days_estimate: Optional[float],
) -> Dict[str, Optional[float] | str]:
    """
    Build the canonical time_delta block.
    """
    total_schedule_delta_days = compute_total_schedule_delta_days(
        base_time_delta_days=base_time_delta_days,
        dead_time_days_estimate=dead_time_days_estimate,
        inspection_reset_days_estimate=inspection_reset_days_estimate,
        resequencing_days_estimate=resequencing_days_estimate,
    )
    cascade_risk_label = _derive_cascade_risk_label(total_schedule_delta_days)

    return {
        "base_time_delta_days": base_time_delta_days,
        "dead_time_days_estimate": dead_time_days_estimate,
        "inspection_reset_days_estimate": inspection_reset_days_estimate,
        "resequencing_days_estimate": resequencing_days_estimate,
        "total_schedule_delta_days": total_schedule_delta_days,
        "cascade_risk_label": cascade_risk_label,
    }
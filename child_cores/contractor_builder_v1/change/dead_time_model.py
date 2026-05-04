"""
Dead-time costing model for contractor_builder_v1 changes.

This module treats idle crew time caused by sequencing disruption, remobilization,
inspection resets, access delays, or trade conflicts as a first-class cost.
"""

from __future__ import annotations

from typing import Dict, Optional


def compute_dead_time_cost_estimate(
    *,
    idle_hours_estimate: Optional[float],
    fully_burdened_rate: Optional[float],
) -> float:
    """
    Compute dead-time cost as idle hours multiplied by a fully burdened hourly rate.
    """
    idle_hours = float(idle_hours_estimate or 0.0)
    burdened_rate = float(fully_burdened_rate or 0.0)
    return round(idle_hours * burdened_rate, 2)


def build_dead_time_cost_block(
    *,
    idle_hours_estimate: Optional[float],
    fully_burdened_rate: Optional[float],
    crew_type: str = "",
    date_range: str = "",
) -> Dict[str, Optional[float] | str]:
    """
    Build the canonical dead-time cost block.
    """
    dead_time_cost_estimate = compute_dead_time_cost_estimate(
        idle_hours_estimate=idle_hours_estimate,
        fully_burdened_rate=fully_burdened_rate,
    )

    return {
        "idle_hours_estimate": idle_hours_estimate,
        "fully_burdened_rate": fully_burdened_rate,
        "crew_type": crew_type,
        "date_range": date_range,
        "dead_time_cost_estimate": dead_time_cost_estimate,
    }
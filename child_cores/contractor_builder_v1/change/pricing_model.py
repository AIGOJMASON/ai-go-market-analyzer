"""
Pricing model for contractor_builder_v1 changes.

This module computes the deterministic cost delta block for a change packet.
It treats dead time as a first-class cost and allows remodel-context disruption
to amplify direct labor cost where appropriate.
"""

from __future__ import annotations

from typing import Dict, Optional


def _safe_amount(value: Optional[float]) -> float:
    if value is None:
        return 0.0
    return float(value)


def compute_total_change_order_amount(
    *,
    material_delta_amount: Optional[float],
    labor_delta_direct_amount: Optional[float],
    labor_inefficiency_multiplier: Optional[float],
    dead_time_cost_estimate: Optional[float],
    supervision_delta_amount: Optional[float],
    general_conditions_delta_amount: Optional[float],
) -> float:
    """
    Compute the total change order amount.

    Formula:
    adjusted direct labor
    + material
    + dead time
    + supervision
    + general conditions
    """
    material = _safe_amount(material_delta_amount)
    labor_direct = _safe_amount(labor_delta_direct_amount)
    inefficiency_multiplier = (
        float(labor_inefficiency_multiplier)
        if labor_inefficiency_multiplier is not None
        else 1.0
    )
    if inefficiency_multiplier <= 0:
        inefficiency_multiplier = 1.0

    adjusted_labor = labor_direct * inefficiency_multiplier
    dead_time = _safe_amount(dead_time_cost_estimate)
    supervision = _safe_amount(supervision_delta_amount)
    general_conditions = _safe_amount(general_conditions_delta_amount)

    total = adjusted_labor + material + dead_time + supervision + general_conditions
    return round(total, 2)


def build_cost_delta_block(
    *,
    material_delta_amount: Optional[float],
    labor_delta_direct_amount: Optional[float],
    labor_inefficiency_multiplier: Optional[float],
    dead_time_hours_estimate: Optional[float],
    dead_time_cost_estimate: Optional[float],
    supervision_delta_amount: Optional[float],
    general_conditions_delta_amount: Optional[float],
) -> Dict[str, Optional[float]]:
    """
    Build the canonical cost_delta block.
    """
    total_change_order_amount = compute_total_change_order_amount(
        material_delta_amount=material_delta_amount,
        labor_delta_direct_amount=labor_delta_direct_amount,
        labor_inefficiency_multiplier=labor_inefficiency_multiplier,
        dead_time_cost_estimate=dead_time_cost_estimate,
        supervision_delta_amount=supervision_delta_amount,
        general_conditions_delta_amount=general_conditions_delta_amount,
    )

    return {
        "material_delta_amount": material_delta_amount,
        "labor_delta_direct_amount": labor_delta_direct_amount,
        "labor_inefficiency_multiplier": labor_inefficiency_multiplier,
        "dead_time_hours_estimate": dead_time_hours_estimate,
        "dead_time_cost_estimate": dead_time_cost_estimate,
        "supervision_delta_amount": supervision_delta_amount,
        "general_conditions_delta_amount": general_conditions_delta_amount,
        "total_change_order_amount": total_change_order_amount,
    }
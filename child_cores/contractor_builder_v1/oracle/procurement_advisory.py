"""
Procurement advisory for contractor_builder_v1.

This module translates oracle projection posture into a simple bounded procurement
advisory. It does not create purchase orders or mutate budgets.
"""

from __future__ import annotations

from typing import Dict, Any

from .oracle_schema import build_procurement_advisory_record


def _derive_procurement_posture(
    projected_pressure_label: str,
    projected_cost_risk_label: str,
    projected_schedule_risk_label: str,
) -> str:
    if projected_pressure_label == "acute":
        return "Escalate_For_PM"
    if "High" in {projected_cost_risk_label, projected_schedule_risk_label}:
        return "Advance_Buy"
    if (
        projected_pressure_label == "elevated"
        or "Moderate" in {projected_cost_risk_label, projected_schedule_risk_label}
    ):
        return "Watch"
    return "Hold"


def build_procurement_advisory(
    *,
    advisory_id: str,
    project_id: str,
    projection: Dict[str, Any],
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a bounded procurement advisory from an oracle projection.
    """
    procurement_posture = _derive_procurement_posture(
        str(projection.get("projected_pressure_label", "")),
        str(projection.get("projected_cost_risk_label", "")),
        str(projection.get("projected_schedule_risk_label", "")),
    )

    justification = (
        f"pressure={projection.get('projected_pressure_label')} | "
        f"cost_risk={projection.get('projected_cost_risk_label')} | "
        f"schedule_risk={projection.get('projected_schedule_risk_label')}"
    )

    return build_procurement_advisory_record(
        advisory_id=advisory_id,
        project_id=project_id,
        market_domain=str(projection["market_domain"]),
        procurement_posture=procurement_posture,
        justification=justification,
        notes=notes,
    )
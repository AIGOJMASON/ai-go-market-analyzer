"""
Risk radar runtime for contractor_builder_v1.

This module aggregates oracle projections into a project-level radar summary.
It preserves domain separation and does not mutate project truth.
"""

from __future__ import annotations

from typing import Dict, List, Any

from .oracle_schema import build_risk_radar_record


def build_risk_radar(
    *,
    radar_id: str,
    project_id: str,
    projections: List[Dict[str, Any]],
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a project-level oracle risk radar from projection records.
    """
    high_domains: List[str] = []
    moderate_domains: List[str] = []
    low_domains: List[str] = []

    for projection in projections:
        domain = str(projection.get("market_domain", ""))
        cost_risk = str(projection.get("projected_cost_risk_label", "Low"))
        schedule_risk = str(projection.get("projected_schedule_risk_label", "Low"))

        if "High" in {cost_risk, schedule_risk}:
            high_domains.append(domain)
        elif "Moderate" in {cost_risk, schedule_risk}:
            moderate_domains.append(domain)
        else:
            low_domains.append(domain)

    if high_domains:
        summary_label = "elevated_external_pressure"
    elif moderate_domains:
        summary_label = "watch_external_pressure"
    else:
        summary_label = "stable_external_pressure"

    return build_risk_radar_record(
        radar_id=radar_id,
        project_id=project_id,
        high_domains=high_domains,
        moderate_domains=moderate_domains,
        low_domains=low_domains,
        summary_label=summary_label,
        notes=notes,
    )
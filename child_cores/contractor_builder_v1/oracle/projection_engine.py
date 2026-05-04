"""
Projection engine for contractor_builder_v1.

This module combines a shock record with a project's exposure profile to build a
bounded oracle projection. It does not forecast exact prices or mutate project state.
"""

from __future__ import annotations

from typing import Dict, Any

from .oracle_schema import build_projection_record


def _normalize_exposure_level(value: str) -> str:
    normalized = str(value).strip().capitalize()
    if normalized == "Low":
        return "Low"
    if normalized == "Moderate":
        return "Moderate"
    if normalized == "High":
        return "High"
    return "Low"


def _project_pressure(shock_severity: str, exposure_level: str) -> str:
    if shock_severity == "high" and exposure_level == "High":
        return "acute"
    if shock_severity in {"moderate", "high"} and exposure_level in {"Moderate", "High"}:
        return "elevated"
    if shock_severity == "low" and exposure_level != "Low":
        return "watch"
    return "stable"


def _project_cost_risk(shock_direction: str, shock_severity: str, exposure_level: str) -> str:
    if shock_direction == "up" and shock_severity == "high" and exposure_level == "High":
        return "High"
    if shock_direction == "up" and exposure_level in {"Moderate", "High"}:
        return "Moderate"
    if shock_direction == "flat":
        return "Low"
    return "Low"


def _project_schedule_risk(shock_severity: str, lead_time_days_estimate: float | None, exposure_level: str) -> str:
    lead_time = float(lead_time_days_estimate or 0.0)
    if exposure_level == "High" and (shock_severity == "high" or lead_time >= 21):
        return "High"
    if exposure_level in {"Moderate", "High"} and (shock_severity == "moderate" or lead_time >= 14):
        return "Moderate"
    return "Low"


def build_oracle_projection(
    *,
    projection_id: str,
    project_id: str,
    snapshot: Dict[str, Any],
    shock_record: Dict[str, Any],
    exposure_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a bounded oracle projection from snapshot + shock + exposure.
    """
    market_domain = str(snapshot["market_domain"])
    exposure_level = _normalize_exposure_level(
        str(exposure_profile.get("domain_exposure", {}).get(market_domain, "Low"))
    )
    shock_direction = str(shock_record["shock_direction"])
    shock_severity = str(shock_record["shock_severity"])

    projected_pressure_label = _project_pressure(shock_severity, exposure_level)
    projected_cost_risk_label = _project_cost_risk(
        shock_direction,
        shock_severity,
        exposure_level,
    )
    projected_schedule_risk_label = _project_schedule_risk(
        shock_severity,
        snapshot.get("lead_time_days_estimate"),
        exposure_level,
    )

    rationale = (
        f"domain={market_domain} | exposure={exposure_level} | "
        f"shock_direction={shock_direction} | shock_severity={shock_severity}"
    )

    return build_projection_record(
        projection_id=projection_id,
        project_id=project_id,
        snapshot_id=str(snapshot["snapshot_id"]),
        exposure_profile_id=str(exposure_profile["exposure_profile_id"]),
        market_domain=market_domain,
        projected_pressure_label=projected_pressure_label,
        projected_cost_risk_label=projected_cost_risk_label,
        projected_schedule_risk_label=projected_schedule_risk_label,
        rationale=rationale,
    )
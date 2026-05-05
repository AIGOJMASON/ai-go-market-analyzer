"""
Oracle schema for contractor_builder_v1.

This module defines the canonical advisory records used for:
- market snapshots
- shock classification
- exposure profiles
- projections
- risk radar summaries
- procurement advisories

Oracle outputs are advisory only. They do not mutate project truth.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

ORACLE_SCHEMA_VERSION = "v1"

MARKET_DOMAIN_ENUM = [
    "Lumber",
    "Steel",
    "Concrete",
    "Electrical",
    "Mechanical",
    "Fuel",
    "Freight",
    "Labor",
    "Drywall",
    "Roofing",
    "General",
]

SHOCK_DIRECTION_ENUM = [
    "up",
    "down",
    "flat",
]

SHOCK_SEVERITY_ENUM = [
    "none",
    "low",
    "moderate",
    "high",
]

EXPOSURE_LEVEL_ENUM = [
    "Low",
    "Moderate",
    "High",
]

PROCUREMENT_POSTURE_ENUM = [
    "Hold",
    "Watch",
    "Advance_Buy",
    "Escalate_For_PM",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_market_snapshot(
    *,
    snapshot_id: str,
    market_domain: str,
    source_label: str,
    reference_date: str,
    price_index_value: Optional[float],
    availability_label: str,
    lead_time_days_estimate: Optional[float],
    volatility_label: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical market snapshot record.
    """
    if market_domain not in MARKET_DOMAIN_ENUM:
        raise ValueError(f"market_domain must be one of {MARKET_DOMAIN_ENUM}")

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "market_domain": market_domain,
        "source_label": source_label,
        "reference_date": reference_date,
        "price_index_value": price_index_value,
        "availability_label": availability_label,
        "lead_time_days_estimate": lead_time_days_estimate,
        "volatility_label": volatility_label,
        "notes": notes,
        "published_at": _utc_now_iso(),
        "allowed_market_domains": MARKET_DOMAIN_ENUM,
    }


def build_shock_record(
    *,
    shock_id: str,
    snapshot_id: str,
    market_domain: str,
    shock_direction: str,
    shock_severity: str,
    trigger_basis: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical shock classification record.
    """
    if market_domain not in MARKET_DOMAIN_ENUM:
        raise ValueError(f"market_domain must be one of {MARKET_DOMAIN_ENUM}")
    if shock_direction not in SHOCK_DIRECTION_ENUM:
        raise ValueError(f"shock_direction must be one of {SHOCK_DIRECTION_ENUM}")
    if shock_severity not in SHOCK_SEVERITY_ENUM:
        raise ValueError(f"shock_severity must be one of {SHOCK_SEVERITY_ENUM}")

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "shock_id": shock_id,
        "snapshot_id": snapshot_id,
        "market_domain": market_domain,
        "shock_direction": shock_direction,
        "shock_severity": shock_severity,
        "trigger_basis": trigger_basis,
        "notes": notes,
        "generated_at": _utc_now_iso(),
        "allowed_directions": SHOCK_DIRECTION_ENUM,
        "allowed_severity": SHOCK_SEVERITY_ENUM,
    }


def build_exposure_profile(
    *,
    exposure_profile_id: str,
    project_id: str,
    domain_exposure: Dict[str, str],
    weighting_notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical project exposure profile.
    """
    for domain, exposure_level in domain_exposure.items():
        if domain not in MARKET_DOMAIN_ENUM:
            raise ValueError(f"Unknown market domain in exposure profile: {domain}")
        if exposure_level not in EXPOSURE_LEVEL_ENUM:
            raise ValueError(
                f"Exposure level must be one of {EXPOSURE_LEVEL_ENUM} for {domain}"
            )

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "exposure_profile_id": exposure_profile_id,
        "project_id": project_id,
        "domain_exposure": dict(domain_exposure),
        "weighting_notes": weighting_notes,
        "generated_at": _utc_now_iso(),
        "allowed_market_domains": MARKET_DOMAIN_ENUM,
        "allowed_exposure_levels": EXPOSURE_LEVEL_ENUM,
    }


def build_projection_record(
    *,
    projection_id: str,
    project_id: str,
    snapshot_id: str,
    exposure_profile_id: str,
    market_domain: str,
    projected_pressure_label: str,
    projected_cost_risk_label: str,
    projected_schedule_risk_label: str,
    rationale: str,
) -> Dict[str, Any]:
    """
    Build a canonical oracle projection record.
    """
    if market_domain not in MARKET_DOMAIN_ENUM:
        raise ValueError(f"market_domain must be one of {MARKET_DOMAIN_ENUM}")

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "projection_id": projection_id,
        "project_id": project_id,
        "snapshot_id": snapshot_id,
        "exposure_profile_id": exposure_profile_id,
        "market_domain": market_domain,
        "projected_pressure_label": projected_pressure_label,
        "projected_cost_risk_label": projected_cost_risk_label,
        "projected_schedule_risk_label": projected_schedule_risk_label,
        "rationale": rationale,
        "generated_at": _utc_now_iso(),
    }


def build_risk_radar_record(
    *,
    radar_id: str,
    project_id: str,
    high_domains: List[str],
    moderate_domains: List[str],
    low_domains: List[str],
    summary_label: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical risk radar summary record.
    """
    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "radar_id": radar_id,
        "project_id": project_id,
        "high_domains": list(high_domains),
        "moderate_domains": list(moderate_domains),
        "low_domains": list(low_domains),
        "summary_label": summary_label,
        "notes": notes,
        "generated_at": _utc_now_iso(),
    }


def build_procurement_advisory_record(
    *,
    advisory_id: str,
    project_id: str,
    market_domain: str,
    procurement_posture: str,
    justification: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical procurement advisory record.
    """
    if market_domain not in MARKET_DOMAIN_ENUM:
        raise ValueError(f"market_domain must be one of {MARKET_DOMAIN_ENUM}")
    if procurement_posture not in PROCUREMENT_POSTURE_ENUM:
        raise ValueError(
            f"procurement_posture must be one of {PROCUREMENT_POSTURE_ENUM}"
        )

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "advisory_id": advisory_id,
        "project_id": project_id,
        "market_domain": market_domain,
        "procurement_posture": procurement_posture,
        "justification": justification,
        "notes": notes,
        "generated_at": _utc_now_iso(),
        "allowed_procurement_posture": PROCUREMENT_POSTURE_ENUM,
    }


def validate_market_snapshot(snapshot: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a market snapshot.
    """
    errors: List[str] = []

    required_fields = [
        "snapshot_id",
        "market_domain",
        "source_label",
        "reference_date",
        "availability_label",
        "volatility_label",
    ]
    for field in required_fields:
        if field not in snapshot:
            errors.append(f"Missing required market snapshot field: {field}")

    if not snapshot.get("snapshot_id"):
        errors.append("snapshot_id may not be empty")
    if not snapshot.get("source_label"):
        errors.append("source_label may not be empty")
    if not snapshot.get("reference_date"):
        errors.append("reference_date may not be empty")

    market_domain = snapshot.get("market_domain")
    if market_domain not in MARKET_DOMAIN_ENUM:
        errors.append(f"market_domain must be one of {MARKET_DOMAIN_ENUM}")

    return errors


def validate_exposure_profile(profile: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of an exposure profile.
    """
    errors: List[str] = []

    required_fields = [
        "exposure_profile_id",
        "project_id",
        "domain_exposure",
    ]
    for field in required_fields:
        if field not in profile:
            errors.append(f"Missing required exposure profile field: {field}")

    if not profile.get("exposure_profile_id"):
        errors.append("exposure_profile_id may not be empty")
    if not profile.get("project_id"):
        errors.append("project_id may not be empty")

    domain_exposure = profile.get("domain_exposure", {})
    if not isinstance(domain_exposure, dict):
        errors.append("domain_exposure must be a mapping")
    else:
        for domain, exposure in domain_exposure.items():
            if domain not in MARKET_DOMAIN_ENUM:
                errors.append(f"Unknown market domain in domain_exposure: {domain}")
            if exposure not in EXPOSURE_LEVEL_ENUM:
                errors.append(
                    f"Exposure level must be one of {EXPOSURE_LEVEL_ENUM} for {domain}"
                )

    return errors


def get_market_snapshot_template() -> Dict[str, Any]:
    """
    Return an empty market snapshot template.
    """
    return deepcopy(
        {
            "schema_version": ORACLE_SCHEMA_VERSION,
            "snapshot_id": "",
            "market_domain": "",
            "source_label": "",
            "reference_date": "",
            "price_index_value": None,
            "availability_label": "",
            "lead_time_days_estimate": None,
            "volatility_label": "",
            "notes": "",
            "published_at": "",
            "allowed_market_domains": MARKET_DOMAIN_ENUM,
        }
    )
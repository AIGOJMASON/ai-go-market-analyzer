"""
Shock classifier for contractor_builder_v1.

This module classifies advisory external pressure from a market snapshot.
It does not predict prices. It only labels bounded pressure posture.
"""

from __future__ import annotations

from typing import Dict, Any

from .oracle_schema import build_shock_record


def _classify_direction(price_index_value: float | None) -> str:
    if price_index_value is None:
        return "flat"
    if price_index_value >= 120:
        return "up"
    if price_index_value <= 95:
        return "down"
    return "flat"


def _classify_severity(
    availability_label: str,
    volatility_label: str,
    lead_time_days_estimate: float | None,
) -> str:
    lead_time = float(lead_time_days_estimate or 0.0)
    tight = availability_label.strip().lower() == "tight"
    high_vol = volatility_label.strip().lower() == "high"

    if tight and (high_vol or lead_time >= 21):
        return "high"
    if tight or high_vol or lead_time >= 14:
        return "moderate"
    if lead_time > 7:
        return "low"
    return "none"


def classify_shock_record(
    *,
    shock_id: str,
    snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a canonical shock record from a published market snapshot.
    """
    market_domain = str(snapshot["market_domain"])
    shock_direction = _classify_direction(snapshot.get("price_index_value"))
    shock_severity = _classify_severity(
        str(snapshot.get("availability_label", "")),
        str(snapshot.get("volatility_label", "")),
        snapshot.get("lead_time_days_estimate"),
    )

    trigger_basis = (
        f"availability={snapshot.get('availability_label')} | "
        f"volatility={snapshot.get('volatility_label')} | "
        f"lead_time_days_estimate={snapshot.get('lead_time_days_estimate')} | "
        f"price_index_value={snapshot.get('price_index_value')}"
    )

    return build_shock_record(
        shock_id=shock_id,
        snapshot_id=str(snapshot["snapshot_id"]),
        market_domain=market_domain,
        shock_direction=shock_direction,
        shock_severity=shock_severity,
        trigger_basis=trigger_basis,
        notes="Deterministic bounded oracle shock classification.",
    )
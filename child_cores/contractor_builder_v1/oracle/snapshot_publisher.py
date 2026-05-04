"""
Snapshot publisher for contractor_builder_v1.

This module converts a raw registry snapshot into a canonical published market
snapshot record. It does not fetch external data or mutate project state.
"""

from __future__ import annotations

from typing import Dict, Any

from .market_snapshot_registry import get_registered_snapshot
from .oracle_schema import build_market_snapshot, validate_market_snapshot


def publish_market_snapshot(snapshot_id: str) -> Dict[str, Any]:
    """
    Publish a canonical market snapshot from the bounded registry.
    """
    raw = get_registered_snapshot(snapshot_id)
    if not raw:
        raise KeyError(f"Unknown oracle snapshot_id: {snapshot_id}")

    snapshot = build_market_snapshot(
        snapshot_id=str(raw["snapshot_id"]),
        market_domain=str(raw["market_domain"]),
        source_label=str(raw["source_label"]),
        reference_date=str(raw["reference_date"]),
        price_index_value=(
            float(raw["price_index_value"])
            if raw.get("price_index_value") is not None
            else None
        ),
        availability_label=str(raw["availability_label"]),
        lead_time_days_estimate=(
            float(raw["lead_time_days_estimate"])
            if raw.get("lead_time_days_estimate") is not None
            else None
        ),
        volatility_label=str(raw["volatility_label"]),
        notes=str(raw.get("notes", "")),
    )

    errors = validate_market_snapshot(snapshot)
    if errors:
        raise ValueError("Invalid published market snapshot: " + "; ".join(errors))

    return snapshot
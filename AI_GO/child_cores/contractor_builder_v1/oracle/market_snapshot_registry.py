"""
Market snapshot registry for contractor_builder_v1.

This module provides a deterministic in-repo registry of example market snapshots.
It is intentionally simple and bounded. It does not fetch live market data.
"""

from __future__ import annotations

from typing import Dict, List, Optional

ORACLE_MARKET_SNAPSHOT_REGISTRY: Dict[str, Dict[str, object]] = {
    "snapshot-lumber-watch": {
        "snapshot_id": "snapshot-lumber-watch",
        "market_domain": "Lumber",
        "source_label": "internal_example_registry",
        "reference_date": "2026-04-14",
        "price_index_value": 112.4,
        "availability_label": "normal",
        "lead_time_days_estimate": 7.0,
        "volatility_label": "moderate",
        "notes": "Illustrative bounded oracle registry snapshot.",
    },
    "snapshot-steel-tight": {
        "snapshot_id": "snapshot-steel-tight",
        "market_domain": "Steel",
        "source_label": "internal_example_registry",
        "reference_date": "2026-04-14",
        "price_index_value": 128.9,
        "availability_label": "tight",
        "lead_time_days_estimate": 21.0,
        "volatility_label": "high",
        "notes": "Illustrative bounded oracle registry snapshot.",
    },
    "snapshot-fuel-flat": {
        "snapshot_id": "snapshot-fuel-flat",
        "market_domain": "Fuel",
        "source_label": "internal_example_registry",
        "reference_date": "2026-04-14",
        "price_index_value": 101.0,
        "availability_label": "normal",
        "lead_time_days_estimate": 2.0,
        "volatility_label": "low",
        "notes": "Illustrative bounded oracle registry snapshot.",
    },
}


def get_registered_snapshot(snapshot_id: str) -> Optional[Dict[str, object]]:
    """
    Return a snapshot from the bounded registry.
    """
    snapshot = ORACLE_MARKET_SNAPSHOT_REGISTRY.get(snapshot_id)
    return dict(snapshot) if snapshot else None


def list_registered_snapshots() -> List[Dict[str, object]]:
    """
    Return all registered snapshots.
    """
    return [dict(snapshot) for snapshot in ORACLE_MARKET_SNAPSHOT_REGISTRY.values()]
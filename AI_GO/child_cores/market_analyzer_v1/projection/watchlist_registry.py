from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


WATCHLIST_REGISTRY: Dict[str, Dict[str, Any]] = {
    "energy": {
        "sector_key": "energy",
        "source_symbol": "XLE",
        "source_type": "sector_watchlist_registry",
        "items": [
            {
                "symbol": "EOG",
                "name": "EOG Resources",
                "role": "beta_upstream",
                "default_bias": "continuation",
                "commodity_driver": "CL",
                "notes": "High-quality upstream name that tends to benefit when an energy rebound becomes a true continuation.",
            },
            {
                "symbol": "OXY",
                "name": "Occidental Petroleum",
                "role": "beta_upstream",
                "default_bias": "two_way_beta",
                "commodity_driver": "CL",
                "notes": "High-beta energy name that can amplify both confirmation and failure.",
            },
            {
                "symbol": "SLB",
                "name": "Schlumberger",
                "role": "services",
                "default_bias": "continuation",
                "commodity_driver": "CL",
                "notes": "Service exposure tends to improve more when energy strength persists beyond the first bounce.",
            },
            {
                "symbol": "XOM",
                "name": "Exxon Mobil",
                "role": "leader_major",
                "default_bias": "confirmation",
                "commodity_driver": "CL",
                "notes": "Large slow leader; useful as confirmation, not ideal as a fragile rebound chase.",
            },
            {
                "symbol": "CVX",
                "name": "Chevron",
                "role": "leader_major",
                "default_bias": "confirmation",
                "commodity_driver": "CL",
                "notes": "Large slow leader; often confirms trends rather than leading weak rebounds.",
            },
            {
                "symbol": "KMI",
                "name": "Kinder Morgan",
                "role": "midstream",
                "default_bias": "low_sensitivity",
                "commodity_driver": "CL",
                "notes": "Less sensitive to a short-lived sector rebound than upstream beta names.",
            },
            {
                "symbol": "MRO",
                "name": "Marathon Oil",
                "role": "failure_beta",
                "default_bias": "fade_if_failure",
                "commodity_driver": "CL",
                "notes": "Higher-beta downside candidate when fragile energy rebounds fail.",
            },
            {
                "symbol": "APA",
                "name": "APA Corporation",
                "role": "failure_beta",
                "default_bias": "fade_if_failure",
                "commodity_driver": "CL",
                "notes": "High-beta downside candidate if sector strength rolls over.",
            },
            {
                "symbol": "XLE",
                "name": "Energy Select Sector SPDR Fund",
                "role": "sector_etf",
                "default_bias": "core_signal",
                "commodity_driver": "CL",
                "notes": "Primary sector signal. Often better as the thing to confirm or fade than to chase.",
            },
            {
                "symbol": "CL",
                "name": "WTI Crude Oil",
                "role": "driver_gate",
                "default_bias": "confirmation_gate",
                "commodity_driver": None,
                "notes": "Root driver for energy. Buy bucket should not be trusted if crude fails to confirm.",
            },
        ],
    }
}


def _safe_lower(value: Any) -> str:
    return str(value or "").strip().lower()


def get_watchlist_registry_for_sector(sector: str) -> Dict[str, Any]:
    sector_key = _safe_lower(sector)
    registry = WATCHLIST_REGISTRY.get(sector_key)
    if not isinstance(registry, dict):
        return {}
    return deepcopy(registry)

from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
        run_external_memory_runtime_path,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge import (
        run_external_memory_runtime_path,
    )


def _normalize_symbol_sector(symbol: str | None, sector: str | None) -> tuple[str, str]:
    """
    Ensure symbol and sector are usable for retrieval/promotion.
    """
    if not symbol or symbol.strip().lower() in {"", "unknown"}:
        symbol = None
    if not sector or sector.strip().lower() in {"", "unknown"}:
        sector = None

    return symbol, sector


def run_market_analyzer_external_memory_path(
    request_id: str,
    symbol: str,
    headline: str,
    price_change_pct: float,
    sector: str,
    confirmation: str,
    event_theme: str | None = None,
    macro_bias: str | None = None,
    route_mode: str | None = None,
    source_type: str = "live_market_input",
) -> Dict[str, Any]:

    # 🔥 FIX — normalize incoming values
    symbol, sector = _normalize_symbol_sector(symbol, sector)

    payload = {
        "request_id": request_id,
        "symbol": symbol,
        "headline": headline,
        "price_change_pct": price_change_pct,
        "sector": sector,
        "confirmation": confirmation,
        "event_theme": event_theme,
        "macro_bias": macro_bias,
        "route_mode": route_mode,
        "source_type": source_type,
        "target_core_id": "market_analyzer_v1",
        "target_child_cores": ["market_analyzer_v1"],
        "origin_surface": "market_analyzer_live",
    }

    return run_external_memory_runtime_path(payload)
from __future__ import annotations

from typing import Any, Dict, Iterable

try:
    from AI_GO.child_cores.market_analyzer_v1.projection.board_snapshot_state import (
        DEFAULT_BOARD_SYMBOLS,
        load_board_snapshot,
    )
except ImportError:
    from child_cores.market_analyzer_v1.projection.board_snapshot_state import (
        DEFAULT_BOARD_SYMBOLS,
        load_board_snapshot,
    )


def build_board_quote_snapshot(
    symbols: Iterable[str] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Read-only cached board snapshot for market board projection.

    This function does NOT fetch from the provider.
    It reads the latest persisted snapshot and prefers the last good cached row,
    even if the most recent provider attempt recorded an error.
    """
    requested = tuple(symbols or DEFAULT_BOARD_SYMBOLS)
    snapshot = load_board_snapshot()
    symbol_map = snapshot.get("symbols")
    if not isinstance(symbol_map, dict):
        symbol_map = {}

    result: Dict[str, Dict[str, Any]] = {}

    for raw_symbol in requested:
        symbol = str(raw_symbol or "").strip().upper()
        if not symbol:
            continue

        row = symbol_map.get(symbol)
        if not isinstance(row, dict):
            result[symbol] = {
                "status": "unavailable",
                "symbol": symbol,
                "price": None,
                "price_change_pct": None,
                "observed_at": None,
                "source": None,
                "cached_at": None,
                "provider_status": None,
                "stale": False,
                "error": "no_cached_snapshot_available",
            }
            continue

        price = row.get("price")
        price_change_pct = row.get("price_change_pct")
        observed_at = row.get("observed_at")
        source = row.get("source")
        cached_at = row.get("cached_at")
        provider_status = row.get("provider_status")
        last_error = row.get("last_error")

        if price is not None:
            result[symbol] = {
                "status": "ok",
                "symbol": symbol,
                "price": price,
                "price_change_pct": price_change_pct,
                "observed_at": observed_at,
                "source": source,
                "cached_at": cached_at,
                "provider_status": provider_status,
                "stale": bool(provider_status == "error"),
                "last_error": last_error,
            }
        else:
            result[symbol] = {
                "status": "unavailable",
                "symbol": symbol,
                "price": None,
                "price_change_pct": None,
                "observed_at": None,
                "source": None,
                "cached_at": cached_at,
                "provider_status": provider_status,
                "stale": False,
                "error": last_error or row.get("error") or "no_cached_snapshot_available",
            }

    return result
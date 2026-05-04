from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

try:
    from AI_GO.child_cores.market_analyzer_v1.data_sources.market_quote_client import (
        AlphaVantageQuoteClient,
    )
    from AI_GO.child_cores.market_analyzer_v1.data_sources.market_quote_policy import (
        MarketQuotePolicy,
    )
    from AI_GO.child_cores.market_analyzer_v1.projection.board_snapshot_state import (
        DEFAULT_BOARD_SYMBOLS,
        next_symbol,
        read_symbol_snapshot,
        upsert_symbol_snapshot,
    )
except ImportError:
    from child_cores.market_analyzer_v1.data_sources.market_quote_client import (
        AlphaVantageQuoteClient,
    )
    from child_cores.market_analyzer_v1.data_sources.market_quote_policy import (
        MarketQuotePolicy,
    )
    from child_cores.market_analyzer_v1.projection.board_snapshot_state import (
        DEFAULT_BOARD_SYMBOLS,
        next_symbol,
        read_symbol_snapshot,
        upsert_symbol_snapshot,
    )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        text = str(value).strip().replace("%", "")
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _build_client() -> AlphaVantageQuoteClient:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("missing_environment_variable:ALPHA_VANTAGE_API_KEY")

    policy = MarketQuotePolicy()
    return AlphaVantageQuoteClient(api_key=api_key, policy=policy)


def _fetch_one(symbol: str) -> Dict[str, Any]:
    client = _build_client()
    raw_quote = client.fetch_global_quote(symbol=symbol)
    quote = raw_quote.payload.get("Global Quote", {})

    price = _safe_float(quote.get("05. price"))
    change_pct = _safe_float(quote.get("10. change percent"))

    row = {
        "symbol": symbol,
        "price": price,
        "price_change_pct": change_pct,
        "observed_at": raw_quote.fetched_at,
        "source": raw_quote.provider,
        "provider_status": "ok",
        "cached_at": _utc_now_iso(),
        "last_error": None,
    }
    upsert_symbol_snapshot(symbol=symbol, row=row)
    return row


def _merge_error_into_existing_row(
    *,
    symbol: str,
    error_text: str,
) -> Dict[str, Any]:
    existing = read_symbol_snapshot(symbol)

    # Preserve last known good data if it exists.
    merged = {
        "symbol": symbol,
        "price": existing.get("price"),
        "price_change_pct": existing.get("price_change_pct"),
        "observed_at": existing.get("observed_at"),
        "source": existing.get("source"),
        "provider_status": "error",
        "cached_at": existing.get("cached_at") or _utc_now_iso(),
        "last_error": error_text,
        "last_attempted_at": _utc_now_iso(),
    }

    # If no prior good row exists, this remains an error-only cache row.
    upsert_symbol_snapshot(symbol=symbol, row=merged)
    return merged


def update_single_symbol(symbol: str) -> Dict[str, Any]:
    normalized = str(symbol or "").strip().upper()
    if not normalized:
        raise ValueError("symbol_required")

    try:
        row = _fetch_one(normalized)
        return {
            "status": "ok",
            "symbol": normalized,
            "row": row,
        }
    except Exception as exc:
        error_text = str(exc)
        row = _merge_error_into_existing_row(
            symbol=normalized,
            error_text=error_text,
        )
        return {
            "status": "error",
            "symbol": normalized,
            "error": error_text,
            "row": row,
        }


def update_rotating_symbol(symbols: Iterable[str] | None = None) -> Dict[str, Any]:
    symbol = next_symbol(symbols or DEFAULT_BOARD_SYMBOLS)
    return update_single_symbol(symbol)


def update_all_symbols(
    symbols: Iterable[str] | None = None,
    *,
    sleep_seconds: float = 1.2,
) -> Dict[str, Any]:
    ordered = [str(s or "").strip().upper() for s in (symbols or DEFAULT_BOARD_SYMBOLS)]
    ordered = [s for s in ordered if s]

    results = []
    for index, symbol in enumerate(ordered):
        result = update_single_symbol(symbol)
        results.append(result)
        if index < len(ordered) - 1:
            time.sleep(sleep_seconds)

    return {
        "status": "completed",
        "count": len(results),
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate the cached market board quote snapshot."
    )
    parser.add_argument("--symbol", help="Update one specific board symbol")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all board symbols sequentially (provider limits still apply)",
    )
    args = parser.parse_args()

    if args.symbol:
        result = update_single_symbol(args.symbol)
    elif args.all:
        result = update_all_symbols()
    else:
        result = update_rotating_symbol()

    print(json.dumps(result, indent=2))
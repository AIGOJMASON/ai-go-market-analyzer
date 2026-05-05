from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from AI_GO.api.market_quote_client import fetch_market_quote


def fetch_alpha_vantage_quote(
    symbol: str,
    *,
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    persist_cache: bool = True,
) -> Dict[str, Any]:
    result = fetch_market_quote(
        symbol,
        fetcher=fetcher,
        persist_cache=persist_cache,
    )
    result["provider_surface"] = "core.providers.alpha_vantage_quote_provider"
    result["advisory_only"] = True
    result["execution_allowed"] = False
    result["recommendation_mutation_allowed"] = False
    return result


def get_quote(
    symbol: str,
    *,
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    persist_cache: bool = True,
) -> Dict[str, Any]:
    return fetch_alpha_vantage_quote(
        symbol,
        fetcher=fetcher,
        persist_cache=persist_cache,
    )
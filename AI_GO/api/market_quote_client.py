from __future__ import annotations

import inspect
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


MUTATION_CLASS = "provider_cache_persistence"
PERSISTENCE_TYPE = "market_quote_provider_cache"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_recommendation": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "bounded_market_quote_source_signal_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_root() -> Path:
    return state_root() / "provider_cache" / "market_quotes"


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "market_quote_provider_cache")
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_payload(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def _safe_symbol(symbol: str) -> str:
    return str(symbol or "").strip().upper()


def _default_fetcher(url: str) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read().decode("utf-8")
    payload = json.loads(body)
    return payload if isinstance(payload, dict) else {}


def fetch_market_quote(
    symbol: str,
    *,
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    persist_cache: bool = True,
) -> Dict[str, Any]:
    clean_symbol = _safe_symbol(symbol)
    if not clean_symbol:
        raise ValueError("symbol is required")

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
    provider = "alpha_vantage"

    if not api_key:
        result: Dict[str, Any] = {
            "status": "unavailable",
            "reason": "missing_alpha_vantage_api_key",
            "symbol": clean_symbol,
            "provider": provider,
            "observed_at": _utc_now_iso(),
        }
    else:
        query = urllib.parse.urlencode(
            {
                "function": "GLOBAL_QUOTE",
                "symbol": clean_symbol,
                "apikey": api_key,
            }
        )
        url = f"https://www.alphavantage.co/query?{query}"
        raw = (fetcher or _default_fetcher)(url)
        quote = raw.get("Global Quote", {}) if isinstance(raw, dict) else {}

        result = {
            "status": "ok" if quote else "empty",
            "provider": provider,
            "symbol": clean_symbol,
            "observed_at": _utc_now_iso(),
            "price": _safe_float(quote.get("05. price")),
            "open": _safe_float(quote.get("02. open")),
            "high": _safe_float(quote.get("03. high")),
            "low": _safe_float(quote.get("04. low")),
            "volume": quote.get("06. volume"),
            "latest_trading_day": quote.get("07. latest trading day"),
            "previous_close": _safe_float(quote.get("08. previous close")),
            "change": _safe_float(quote.get("09. change")),
            "change_percent": quote.get("10. change percent"),
            "raw_provider_keys": sorted(raw.keys()) if isinstance(raw, dict) else [],
        }

    normalized = _normalize_payload(result)

    if persist_cache:
        path = _cache_root() / f"{clean_symbol}.json"
        normalized["cache_path"] = _governed_write(path, normalized)

    return normalized


def get_quote(
    symbol: str,
    *,
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    persist_cache: bool = True,
) -> Dict[str, Any]:
    return fetch_market_quote(
        symbol,
        fetcher=fetcher,
        persist_cache=persist_cache,
    )
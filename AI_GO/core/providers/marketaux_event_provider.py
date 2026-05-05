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


MUTATION_CLASS = "source_signal_persistence"
PERSISTENCE_TYPE = "marketaux_event_provider_cache"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_recommendation": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "bounded_market_event_source_signal_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_root() -> Path:
    return state_root() / "provider_cache" / "marketaux_events"


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "marketaux_event_provider_cache")
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


def _default_fetcher(url: str) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read().decode("utf-8")
    payload = json.loads(body)
    return payload if isinstance(payload, dict) else {}


def fetch_marketaux_events(
    *,
    symbols: str = "",
    keywords: str = "",
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    persist_cache: bool = True,
) -> Dict[str, Any]:
    token = os.getenv("MARKETAUX_API_KEY", "").strip() or os.getenv("AI_GO_MARKETAUX_API_KEY", "").strip()

    if not token:
        result = {
            "status": "unavailable",
            "reason": "missing_marketaux_api_key",
            "provider": "marketaux",
            "observed_at": _utc_now_iso(),
            "symbols": symbols,
            "keywords": keywords,
            "events": [],
        }
    else:
        query = urllib.parse.urlencode(
            {
                "api_token": token,
                "symbols": symbols,
                "search": keywords,
                "language": "en",
                "limit": "10",
            }
        )
        url = f"https://api.marketaux.com/v1/news/all?{query}"
        raw = (fetcher or _default_fetcher)(url)
        events = raw.get("data", []) if isinstance(raw, dict) else []

        result = {
            "status": "ok",
            "provider": "marketaux",
            "observed_at": _utc_now_iso(),
            "symbols": symbols,
            "keywords": keywords,
            "event_count": len(events) if isinstance(events, list) else 0,
            "events": events if isinstance(events, list) else [],
        }

    normalized = _normalize_payload(result)

    if persist_cache:
        safe_name = (symbols or keywords or "marketaux_events").replace("/", "_").replace("\\", "_").replace(" ", "_")
        normalized["cache_path"] = _governed_write(_cache_root() / f"{safe_name}.json", normalized)

    return normalized


def get_events(**kwargs: Any) -> Dict[str, Any]:
    return fetch_marketaux_events(**kwargs)


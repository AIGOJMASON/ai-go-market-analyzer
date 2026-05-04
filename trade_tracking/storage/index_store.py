from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root
from AI_GO.trade_tracking.trade_tracking_registry import INDEX_FILE_NAMES


MUTATION_CLASS = "trade_tracking_persistence"
PERSISTENCE_TYPE = "trade_tracking_index"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_source_events": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "trade_tracking_rebuildable_index",
}


def _trade_tracking_root() -> Path:
    return state_root() / "trade_tracking"


def _index_dir() -> Path:
    return _trade_tracking_root() / "db" / "indexes"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

    if isinstance(payload, dict) and payload.get("artifact_type") == "governed_persistence_envelope":
        return payload.get("payload", default)

    if isinstance(payload, dict) and "items" in payload:
        return payload.get("items", default)

    return payload


def _normalize_index(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "trade_tracking_index")
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = False
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["derived_from_events"] = True
    normalized["rebuildable"] = True
    normalized["execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_index(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": False,
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


def _write_json(path: Path, payload: Any) -> str:
    if isinstance(payload, dict):
        body = _normalize_index(payload)
    else:
        body = {
            "artifact_type": "trade_tracking_index",
            "items": payload,
        }
    return _governed_write(path, body)


def update_indexes(event_record: Dict[str, Any], event_path: Path) -> None:
    idx_dir = _index_dir()

    by_trade_path = idx_dir / INDEX_FILE_NAMES["by_trade_id"]
    by_symbol_path = idx_dir / INDEX_FILE_NAMES["by_symbol"]
    by_system_path = idx_dir / INDEX_FILE_NAMES["by_system_id"]
    latest_path = idx_dir / INDEX_FILE_NAMES["latest_events"]

    by_trade = _load_json(by_trade_path, {})
    by_symbol = _load_json(by_symbol_path, {})
    by_system = _load_json(by_system_path, {})
    latest = _load_json(latest_path, [])

    if not isinstance(by_trade, dict):
        by_trade = {}
    if not isinstance(by_symbol, dict):
        by_symbol = {}
    if not isinstance(by_system, dict):
        by_system = {}
    if not isinstance(latest, list):
        latest = []

    event_id = str(event_record.get("event_id", "")).strip()
    trade_id = str(event_record.get("trade_id", "")).strip()
    symbol = str(event_record.get("symbol", "")).strip().upper()
    system_id = str(event_record.get("system_id", "")).strip()

    event_ref = {
        "event_id": event_id,
        "trade_id": trade_id,
        "event_path": str(event_path),
        "path": str(event_path),
        "timestamp": event_record.get("timestamp"),
        "event_type": event_record.get("event_type"),
        "symbol": symbol,
        "system_id": system_id,
    }

    if trade_id:
        by_trade.setdefault(trade_id, [])
        if event_ref not in by_trade[trade_id]:
            by_trade[trade_id].append(event_ref)

    if symbol:
        by_symbol.setdefault(symbol, [])
        if event_ref not in by_symbol[symbol]:
            by_symbol[symbol].append(event_ref)

    if system_id:
        by_system.setdefault(system_id, [])
        if event_ref not in by_system[system_id]:
            by_system[system_id].append(event_ref)

    latest = [item for item in latest if isinstance(item, dict) and item.get("event_id") != event_id]
    latest.insert(0, event_ref)
    latest = sorted(latest, key=lambda item: str(item.get("timestamp", "")), reverse=True)[:200]

    _write_json(by_trade_path, {"index_name": "by_trade_id", "items": by_trade})
    _write_json(by_symbol_path, {"index_name": "by_symbol", "items": by_symbol})
    _write_json(by_system_path, {"index_name": "by_system_id", "items": by_system})
    _write_json(latest_path, {"index_name": "latest_events", "items": latest})


def write_index(index_name: str, items: Any) -> str:
    file_name = INDEX_FILE_NAMES[index_name]
    return _write_json(_index_dir() / file_name, {"index_name": index_name, "items": items})


def rebuild_indexes(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_trade_id: Dict[str, List[Dict[str, Any]]] = {}
    by_symbol: Dict[str, List[Dict[str, Any]]] = {}
    by_system_id: Dict[str, List[Dict[str, Any]]] = {}

    latest_events: List[Dict[str, Any]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        event_ref = {
            "event_id": event.get("event_id"),
            "trade_id": event.get("trade_id"),
            "event_type": event.get("event_type"),
            "timestamp": event.get("timestamp"),
            "symbol": event.get("symbol"),
            "system_id": event.get("system_id"),
        }

        trade_id = str(event.get("trade_id", "")).strip()
        symbol = str(event.get("symbol", "")).strip().upper()
        system_id = str(event.get("system_id", "")).strip()

        if trade_id:
            by_trade_id.setdefault(trade_id, []).append(event_ref)
        if symbol:
            by_symbol.setdefault(symbol, []).append(event_ref)
        if system_id:
            by_system_id.setdefault(system_id, []).append(event_ref)

        latest_events.append(event_ref)

    latest_events = sorted(
        latest_events,
        key=lambda item: str(item.get("timestamp", "")),
        reverse=True,
    )[:100]

    results = {
        "by_trade_id": write_index("by_trade_id", by_trade_id),
        "by_symbol": write_index("by_symbol", by_symbol),
        "by_system_id": write_index("by_system_id", by_system_id),
        "latest_events": write_index("latest_events", {"events": latest_events}),
    }

    return {
        "status": "rebuilt",
        "event_count": len(events),
        "indexes": results,
    }

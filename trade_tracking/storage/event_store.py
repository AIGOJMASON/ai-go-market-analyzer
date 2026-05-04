from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


MUTATION_CLASS = "trade_tracking_persistence"
PERSISTENCE_TYPE = "trade_tracking_event"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "trade_tracking_event_append_only",
}


def _trade_tracking_root() -> Path:
    return state_root() / "trade_tracking"


def _event_root() -> Path:
    return _trade_tracking_root() / "db" / "events"


def _monthly_events_dir(timestamp: str) -> Path:
    year_month = str(timestamp or "")[:7] or "unknown"
    return _event_root() / year_month


def _normalize_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "trade_tracking_event")
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = False
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["append_only"] = True
    normalized["execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_event(payload)

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


def write_event_record(event_record: Dict[str, Any]) -> Path:
    normalized = _normalize_event(event_record)

    timestamp = str(normalized.get("timestamp", "")).strip()
    event_id = str(normalized.get("event_id", "")).strip()

    if not timestamp:
        raise ValueError("timestamp is required")
    if not event_id:
        raise ValueError("event_id is required")

    target_dir = _monthly_events_dir(timestamp)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f"{event_id}.json"
    _governed_write(target_path, normalized)

    return target_path


def event_path(event_id: str) -> Path:
    clean_id = str(event_id or "").strip()
    if not clean_id:
        raise ValueError("event_id is required")

    root = _event_root()
    if root.exists():
        for path in root.glob(f"*/{clean_id}.json"):
            return path

    return root / "unknown" / f"{clean_id}.json"


def write_event(event: Dict[str, Any]) -> Dict[str, Any]:
    path = write_event_record(event)
    normalized = _normalize_event(event)

    return {
        "status": "persisted",
        "event_id": str(normalized.get("event_id", "")),
        "event_path": str(path),
        "event_record": normalized,
    }


def read_event(event_id: str) -> Dict[str, Any]:
    path = event_path(event_id)
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def list_events() -> List[Dict[str, Any]]:
    root = _event_root()
    if not root.exists():
        return []

    events: List[Dict[str, Any]] = []

    for path in sorted(root.glob("*/*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(payload, dict):
            events.append(payload)

    return events
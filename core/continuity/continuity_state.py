from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "continuity_state"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "continuity_memory_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_continuity_state_path() -> Path:
    return get_project_root() / "state" / "smi" / "current" / "smi_state.json"


def _default_state() -> Dict[str, Any]:
    return {
        "artifact_type": "continuity_state",
        "artifact_version": "v1",
        "status": "active",
        "last_updated": None,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "continuity_keys": {},
        "events": [],
    }


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Continuity state must decode to a dict")

    return payload


def _normalize_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    state = dict(payload)

    state.setdefault("artifact_type", "continuity_state")
    state.setdefault("artifact_version", "v1")
    state.setdefault("status", "active")
    state.setdefault("last_updated", None)
    state.setdefault("continuity_keys", {})
    state.setdefault("events", [])

    state["persistence_type"] = PERSISTENCE_TYPE
    state["mutation_class"] = MUTATION_CLASS
    state["advisory_only"] = True
    state["authority_metadata"] = dict(AUTHORITY_METADATA)

    if not isinstance(state["continuity_keys"], dict):
        raise ValueError("continuity_keys must be a dict")

    if not isinstance(state["events"], list):
        raise ValueError("events must be a list")

    return state


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
    kwargs = {
        "path": path,
        "output_path": path,
        "payload": payload,
        "data": payload,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        return governed_write_json(**kwargs)

    if accepted:
        return governed_write_json(**accepted)

    return governed_write_json(path, payload)


def load_continuity_state() -> Dict[str, Any]:
    return _normalize_state(_read_json(get_continuity_state_path(), _default_state()))


def save_continuity_state(state: Dict[str, Any]) -> str:
    normalized = _normalize_state(state)
    path = get_continuity_state_path()

    result = _governed_write(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def record_continuity_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("event must be a dict")

    state = load_continuity_state()
    events = list(state.get("events", []))
    continuity_keys = dict(state.get("continuity_keys", {}))

    normalized_event = dict(event)
    normalized_event.setdefault("recorded_at", _utc_now_iso())
    normalized_event.setdefault("persistence_type", "continuity_event")
    normalized_event.setdefault("mutation_class", MUTATION_CLASS)
    normalized_event.setdefault("advisory_only", True)
    normalized_event.setdefault("authority_metadata", dict(AUTHORITY_METADATA))

    key = str(
        normalized_event.get("continuity_key")
        or normalized_event.get("event_key")
        or normalized_event.get("event_class")
        or "unclassified_continuity_event"
    ).strip()

    current = dict(continuity_keys.get(key, {}))
    current["continuity_key"] = key
    current["recurrence_count"] = int(current.get("recurrence_count", 0)) + 1
    current["last_seen_timestamp"] = normalized_event.get("recorded_at")
    current["source_surface"] = normalized_event.get("source_surface", current.get("source_surface", "unknown"))
    current["event_class"] = normalized_event.get("event_class", current.get("event_class", "unknown"))
    current["symbol"] = normalized_event.get("symbol", current.get("symbol", ""))
    current["event_theme"] = normalized_event.get("event_theme", current.get("event_theme", ""))

    continuity_keys[key] = current
    events.append(normalized_event)

    state["events"] = events[-500:]
    state["continuity_keys"] = continuity_keys
    state["last_updated"] = normalized_event.get("recorded_at")

    state_path = save_continuity_state(state)

    return {
        "status": "recorded",
        "state_path": state_path,
        "continuity_key": key,
        "event": normalized_event,
    }


def update_continuity_state(event: Dict[str, Any]) -> Dict[str, Any]:
    return record_continuity_event(event)
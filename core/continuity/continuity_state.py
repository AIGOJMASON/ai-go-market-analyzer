from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_smi_state_path() -> Path:
    return get_project_root() / "state" / "smi" / "current" / "smi_state.json"


def _default_state() -> Dict[str, Any]:
    return {
        "status": "active",
        "last_updated": None,
        "events": [],
    }


def load_smi_state() -> Dict[str, Any]:
    path = get_smi_state_path()

    if not path.exists():
        return _default_state()

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("SMI state must decode to a dict")

    payload.setdefault("status", "active")
    payload.setdefault("last_updated", None)
    payload.setdefault("events", [])

    if not isinstance(payload["events"], list):
        raise ValueError("SMI state events field must be a list")

    return payload


def save_smi_state(state: Dict[str, Any]) -> str:
    path = get_smi_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)

    return str(path)


def append_smi_event(event: Dict[str, Any]) -> Dict[str, Any]:
    state = load_smi_state()
    events = list(state.get("events", []))
    events.append(event)

    state["events"] = events
    state["last_updated"] = event.get("recorded_at")

    state_path = save_smi_state(state)

    return {
        "status": "recorded",
        "state_path": state_path,
        "event_index": len(events) - 1,
        "event": event,
    }
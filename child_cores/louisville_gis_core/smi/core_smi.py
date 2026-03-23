from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "louisville_gis_core"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_core_root() -> Path:
    return get_project_root() / "child_cores" / CORE_ID


def get_state_path() -> Path:
    return get_core_root() / "state" / "current" / "core_smi_state.json"


def _default_state() -> Dict[str, Any]:
    return {
        "core_id": CORE_ID,
        "status": "active",
        "last_updated": None,
        "events": [],
    }


def load_core_state() -> Dict[str, Any]:
    path = get_state_path()

    if not path.exists():
        return _default_state()

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Louisville GIS core SMI state must decode to a dict")

    payload.setdefault("core_id", CORE_ID)
    payload.setdefault("status", "active")
    payload.setdefault("last_updated", None)
    payload.setdefault("events", [])

    if not isinstance(payload["events"], list):
        raise ValueError("Louisville GIS core SMI events field must be a list")

    return payload


def save_core_state(state: Dict[str, Any]) -> str:
    path = get_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return str(path)


def record_verified_execution(
    *,
    receipt_path: str,
    watcher_result: Dict[str, Any],
    execution_record_path: str,
    output_path: str,
) -> Dict[str, Any]:
    """
    Legacy surface retired for Stage 23 compliance.

    Continuity mutation may not be invoked from legacy child-core execution
    flow. Continuity must be introduced only by a later governed stage.
    """
    event = {
        "event_type": "continuity_invocation_blocked",
        "recorded_at": _utc_now_iso(),
        "core_id": CORE_ID,
        "receipt_path": receipt_path,
        "execution_record_path": execution_record_path,
        "output_path": output_path,
        "watcher_status": watcher_result.get("status"),
        "reason": "continuity_invocation_not_lawful_before_governed_continuity_stage",
        "allowed_future_boundary": "stage25_continuity",
    }

    state = load_core_state()
    events = list(state.get("events", []))
    events.append(event)
    state["events"] = events
    state["last_updated"] = event["recorded_at"]

    state_path = save_core_state(state)

    return {
        "status": "blocked",
        "state_path": state_path,
        "event_index": len(events) - 1,
        "event": event,
    }
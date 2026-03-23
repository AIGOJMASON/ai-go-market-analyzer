from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
TRANSITIONS_PATH = ROOT / "state" / "monitoring" / "current" / "transitions.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _default_transitions() -> Dict[str, Any]:
    return {
        "transition_log_id": "AI_GO_RUNTIME_TRANSITIONS",
        "updated_at": _utc_now(),
        "items": [],
    }


def record_transition(packet_id: str, phase: str, status: str, details: Dict[str, Any] | None = None) -> str:
    log = _read_json(TRANSITIONS_PATH, _default_transitions())
    item = {
        "packet_id": packet_id,
        "phase": phase,
        "status": status,
        "details": details or {},
        "recorded_at": _utc_now(),
    }
    log["items"].append(item)
    log["updated_at"] = _utc_now()
    _write_json(TRANSITIONS_PATH, log)
    return TRANSITIONS_PATH.as_posix()
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
SENTINEL_STATUS_PATH = ROOT / "state" / "monitoring" / "current" / "sentinel_status.json"
TRANSITIONS_PATH = ROOT / "state" / "monitoring" / "current" / "transitions.json"
UNRESOLVED_PATH = ROOT / "state" / "smi" / "current" / "unresolved_queue.json"


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


def evaluate_runtime_health(packet_id: str) -> Dict[str, Any]:
    transitions = _read_json(TRANSITIONS_PATH, {"items": []})
    unresolved = _read_json(UNRESOLVED_PATH, {"items": []})

    recent_items = [item for item in transitions.get("items", []) if item.get("packet_id") == packet_id]
    unresolved_count = len(unresolved.get("items", []))
    ambiguous_count = sum(
        1
        for item in recent_items
        if item.get("phase") == "routing"
        and item.get("status") in {"ambiguous", "inactive_target", "forbidden_route"}
    )

    health = "warning" if ambiguous_count > 0 or unresolved_count >= 3 else "ok"

    payload = {
        "packet_id": packet_id,
        "health": health,
        "recent_transition_count": len(recent_items),
        "unresolved_count": unresolved_count,
        "ambiguous_routing_count": ambiguous_count,
        "evaluated_at": _utc_now(),
    }
    _write_json(SENTINEL_STATUS_PATH, payload)
    return {
        "status": "evaluated",
        "health": health,
        "sentinel_status_path": SENTINEL_STATUS_PATH.as_posix(),
    }
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
UNRESOLVED_CURRENT_PATH = ROOT / "state" / "smi" / "current" / "unresolved_queue.json"
UNRESOLVED_ARCHIVE_PATH = ROOT / "state" / "smi" / "unresolved" / "unresolved_queue.json"


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


def _default_queue() -> Dict[str, Any]:
    return {
        "queue_id": "AI_GO_UNRESOLVED_QUEUE",
        "updated_at": _utc_now(),
        "items": [],
    }


def load_unresolved_queue() -> Dict[str, Any]:
    return _read_json(UNRESOLVED_CURRENT_PATH, _default_queue())


def save_unresolved_queue(queue: Dict[str, Any]) -> None:
    queue["updated_at"] = _utc_now()
    _write_json(UNRESOLVED_CURRENT_PATH, queue)
    _write_json(UNRESOLVED_ARCHIVE_PATH, queue)


def enqueue_unresolved_route(payload: Dict[str, Any]) -> str:
    queue = load_unresolved_queue()
    item = {
        "unresolved_id": f"{payload['packet_id']}__routing_unresolved",
        "type": "routing_unresolved",
        "packet_id": payload["packet_id"],
        "routing_status": payload.get("routing_status"),
        "routing_reason": payload.get("routing_reason"),
        "routing_confidence": payload.get("routing_confidence", 0.0),
        "routing_decision_path": payload.get("routing_decision_path"),
        "created_at": _utc_now(),
    }
    queue["items"].append(item)
    save_unresolved_queue(queue)
    return UNRESOLVED_CURRENT_PATH.as_posix()
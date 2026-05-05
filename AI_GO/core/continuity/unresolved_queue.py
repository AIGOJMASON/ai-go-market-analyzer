from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "unresolved_continuity_queue"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "continuity_memory_only",
}


ROOT = Path(__file__).resolve().parents[2]
UNRESOLVED_CURRENT_PATH = ROOT / "state" / "smi" / "current" / "unresolved_queue.json"
UNRESOLVED_ARCHIVE_PATH = ROOT / "state" / "smi" / "unresolved" / "unresolved_queue.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _default_queue() -> Dict[str, Any]:
    return {
        "artifact_type": "unresolved_continuity_queue",
        "artifact_version": "v1",
        "queue_id": "AI_GO_UNRESOLVED_QUEUE",
        "updated_at": _utc_now(),
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "items": [],
    }


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Unresolved queue must decode to a dict")

    return payload


def _normalize_queue(payload: Dict[str, Any]) -> Dict[str, Any]:
    queue = dict(payload)

    queue.setdefault("artifact_type", "unresolved_continuity_queue")
    queue.setdefault("artifact_version", "v1")
    queue.setdefault("queue_id", "AI_GO_UNRESOLVED_QUEUE")
    queue.setdefault("updated_at", _utc_now())
    queue.setdefault("items", [])

    queue["persistence_type"] = PERSISTENCE_TYPE
    queue["mutation_class"] = MUTATION_CLASS
    queue["advisory_only"] = True
    queue["authority_metadata"] = dict(AUTHORITY_METADATA)

    if not isinstance(queue["items"], list):
        raise ValueError("Unresolved queue items field must be a list")

    return queue


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


def load_unresolved_queue() -> Dict[str, Any]:
    return _normalize_queue(_read_json(UNRESOLVED_CURRENT_PATH, _default_queue()))


def save_unresolved_queue(queue: Dict[str, Any]) -> Dict[str, str]:
    normalized = _normalize_queue(queue)
    normalized["updated_at"] = _utc_now()

    current_result = _governed_write(UNRESOLVED_CURRENT_PATH, normalized)
    archive_result = _governed_write(UNRESOLVED_ARCHIVE_PATH, normalized)

    return {
        "current_queue_path": str(
            current_result.get("path")
            if isinstance(current_result, dict) and current_result.get("path")
            else UNRESOLVED_CURRENT_PATH
        ),
        "archive_queue_path": str(
            archive_result.get("path")
            if isinstance(archive_result, dict) and archive_result.get("path")
            else UNRESOLVED_ARCHIVE_PATH
        ),
    }


def enqueue_unresolved_route(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    queue = load_unresolved_queue()

    packet_id = str(payload.get("packet_id", "")).strip()
    if not packet_id:
        raise ValueError("packet_id is required")

    item = {
        "unresolved_id": f"{packet_id}__routing_unresolved",
        "type": "routing_unresolved",
        "packet_id": packet_id,
        "routing_status": payload.get("routing_status"),
        "routing_reason": payload.get("routing_reason"),
        "routing_confidence": payload.get("routing_confidence", 0.0),
        "routing_decision_path": payload.get("routing_decision_path"),
        "created_at": _utc_now(),
        "persistence_type": "unresolved_queue_item",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    queue["items"].append(item)
    paths = save_unresolved_queue(queue)

    return paths["current_queue_path"]


def enqueue_unresolved_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    queue = load_unresolved_queue()

    unresolved_id = str(payload.get("unresolved_id") or payload.get("id") or "").strip()
    if not unresolved_id:
        unresolved_id = f"unresolved_{len(queue.get('items', [])) + 1}_{_utc_now()}"

    item = dict(payload)
    item["unresolved_id"] = unresolved_id
    item.setdefault("created_at", _utc_now())
    item.setdefault("persistence_type", "unresolved_queue_item")
    item.setdefault("mutation_class", MUTATION_CLASS)
    item.setdefault("advisory_only", True)
    item.setdefault("authority_metadata", dict(AUTHORITY_METADATA))

    queue["items"].append(item)
    paths = save_unresolved_queue(queue)

    return {
        "status": "queued",
        "id": unresolved_id,
        **paths,
    }
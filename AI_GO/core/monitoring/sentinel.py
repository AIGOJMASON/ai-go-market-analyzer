from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "monitoring_sentinel_status"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "monitoring_awareness_only",
}

ROOT = Path(__file__).resolve().parents[2]
SENTINEL_STATUS_PATH = ROOT / "state" / "monitoring" / "current" / "sentinel_status.json"
TRANSITIONS_PATH = ROOT / "state" / "monitoring" / "current" / "transitions.json"
UNRESOLVED_PATH = ROOT / "state" / "smi" / "current" / "unresolved_queue.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized["artifact_type"] = "sentinel_status"
    normalized["artifact_version"] = "v1"
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
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
        return governed_write_json(**kwargs)

    if accepted:
        return governed_write_json(**accepted)

    return governed_write_json(path, normalized)


def evaluate_runtime_health(packet_id: str) -> Dict[str, Any]:
    transitions = _read_json(TRANSITIONS_PATH, {"items": []})
    unresolved = _read_json(UNRESOLVED_PATH, {"items": []})

    recent_items = [
        item
        for item in transitions.get("items", [])
        if isinstance(item, dict) and item.get("packet_id") == packet_id
    ]

    unresolved_items = unresolved.get("items", [])
    unresolved_count = len(unresolved_items) if isinstance(unresolved_items, list) else 0

    ambiguous_count = sum(
        1
        for item in recent_items
        if item.get("phase") == "routing"
        and item.get("status") in {"ambiguous", "inactive_target", "forbidden_route"}
    )

    health = "stable"
    if unresolved_count or ambiguous_count:
        health = "attention_required"

    payload = {
        "packet_id": packet_id,
        "health": health,
        "recent_transition_count": len(recent_items),
        "unresolved_count": unresolved_count,
        "ambiguous_routing_count": ambiguous_count,
        "evaluated_at": _utc_now(),
    }

    result = _governed_write(SENTINEL_STATUS_PATH, payload)

    return {
        "status": "evaluated",
        "health": health,
        "sentinel_status_path": str(
            result.get("path")
            if isinstance(result, dict) and result.get("path")
            else SENTINEL_STATUS_PATH
        ),
    }
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "continuity_change_ledger"

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


def get_change_ledger_path() -> Path:
    return get_project_root() / "state" / "smi" / "current" / "change_ledger.json"


def _default_ledger() -> Dict[str, Any]:
    return {
        "artifact_type": "continuity_change_ledger",
        "artifact_version": "v1",
        "status": "active",
        "last_updated": None,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "changes": [],
    }


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Change ledger must decode to a dict")

    return payload


def _normalize_ledger(payload: Dict[str, Any]) -> Dict[str, Any]:
    ledger = dict(payload)

    ledger.setdefault("artifact_type", "continuity_change_ledger")
    ledger.setdefault("artifact_version", "v1")
    ledger.setdefault("status", "active")
    ledger.setdefault("last_updated", None)
    ledger.setdefault("changes", [])

    ledger["persistence_type"] = PERSISTENCE_TYPE
    ledger["mutation_class"] = MUTATION_CLASS
    ledger["advisory_only"] = True
    ledger["authority_metadata"] = dict(AUTHORITY_METADATA)

    if not isinstance(ledger["changes"], list):
        raise ValueError("Change ledger changes field must be a list")

    return ledger


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


def load_change_ledger() -> Dict[str, Any]:
    return _normalize_ledger(_read_json(get_change_ledger_path(), _default_ledger()))


def save_change_ledger(ledger: Dict[str, Any]) -> str:
    normalized = _normalize_ledger(ledger)
    path = get_change_ledger_path()

    result = _governed_write(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def record_change(change: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(change, dict):
        raise ValueError("change must be a dict")

    ledger = load_change_ledger()
    changes = list(ledger.get("changes", []))

    normalized_change = dict(change)
    normalized_change.setdefault("recorded_at", _utc_now_iso())
    normalized_change.setdefault("persistence_type", "continuity_change_record")
    normalized_change.setdefault("mutation_class", MUTATION_CLASS)
    normalized_change.setdefault("advisory_only", True)
    normalized_change.setdefault("authority_metadata", dict(AUTHORITY_METADATA))

    changes.append(normalized_change)

    ledger["changes"] = changes
    ledger["last_updated"] = normalized_change.get("recorded_at")

    ledger_path = save_change_ledger(ledger)

    return {
        "status": "recorded",
        "ledger_path": ledger_path,
        "change_index": len(changes) - 1,
        "change": normalized_change,
    }
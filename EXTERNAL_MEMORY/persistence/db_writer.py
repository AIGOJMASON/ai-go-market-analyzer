
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "external_memory_record"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_runtime": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "external_memory_append_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _memory_root() -> Path:
    return state_root() / "external_memory"


def _memory_path() -> Path:
    return _memory_root() / "external_memory_records.json"


def _normalize_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    normalized.setdefault("artifact_type", "external_memory_record")
    normalized.setdefault("recorded_at", _utc_now_iso())
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = dict(payload)
    normalized["persistence_type"] = "external_memory_store"
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": "external_memory_store",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
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


def _read_store() -> Dict[str, Any]:
    path = _memory_path()
    if not path.exists():
        return {
            "artifact_type": "external_memory_store",
            "artifact_version": "northstar_external_memory_v1",
            "records": [],
            "persistence_type": "external_memory_store",
            "mutation_class": MUTATION_CLASS,
            "advisory_only": True,
            "authority_metadata": dict(AUTHORITY_METADATA),
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"records": []}


def write_memory_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    store = _read_store()
    records = store.get("records", [])
    if not isinstance(records, list):
        records = []

    normalized_record = _normalize_record(record)
    records.append(normalized_record)

    store["records"] = records[-10000:]
    store["updated_at"] = _utc_now_iso()

    path = _governed_write(_memory_path(), store)

    return {
        "status": "persisted",
        "path": path,
        "record": normalized_record,
    }


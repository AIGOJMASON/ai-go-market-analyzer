from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "smi_continuity_write_path"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "smi_continuity_memory_only",
}


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_smi_current_root() -> Path:
    return get_project_root() / "state" / "smi" / "current"


def _normalize_payload(payload: Dict[str, Any], persistence_type: str) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    normalized = dict(payload)
    normalized.setdefault("artifact_type", persistence_type)
    normalized.setdefault("artifact_version", "v1")
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any], persistence_type: str) -> Any:
    normalized = _normalize_payload(payload, persistence_type)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
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

    return governed_write_json(path, normalized)


def write_smi_json(filename: str, payload: Dict[str, Any]) -> str:
    clean_filename = str(filename or "").strip()
    if not clean_filename:
        raise ValueError("filename is required")

    if not clean_filename.endswith(".json"):
        clean_filename = f"{clean_filename}.json"

    path = get_smi_current_root() / clean_filename
    persistence_type = f"{PERSISTENCE_TYPE}:{clean_filename}"

    result = _governed_write(path, payload, persistence_type)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def persist_smi_state(payload: Dict[str, Any]) -> str:
    return write_smi_json("smi_state.json", payload)


def persist_smi_snapshot(filename: str, payload: Dict[str, Any]) -> str:
    return write_smi_json(filename, payload)
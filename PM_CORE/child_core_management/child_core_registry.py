from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parents[1]
AI_GO_ROOT = PM_CORE_DIR.parent
CHILD_CORES_DIR = AI_GO_ROOT / "child_cores"

STATE_DIR = PM_CORE_DIR / "state"
CURRENT_DIR = STATE_DIR / "current"

AUTHORITATIVE_REGISTRY_PATH = CURRENT_DIR / "child_core_registry.json"
MIRROR_REGISTRY_PATH = CHILD_CORES_DIR / "_child_core_registry_mirror.json"

REGISTRY_VERSION = "northstar_child_core_registry_v1"
MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "pm_child_core_registry"

REQUIRED_DIRECTORIES = ["api", "state", "watcher", "smi"]
REQUIRED_FILES = ["CORE_IDENTITY.md", "INHERITANCE_CONTRACT.md"]

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_activate_child_core_without_governance": False,
    "can_retire_child_core_without_governance": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_child_core_registry_memory_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_payload(payload: Dict[str, Any], persistence_type: str = PERSISTENCE_TYPE) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", persistence_type)
    normalized.setdefault("artifact_version", REGISTRY_VERSION)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["approval_required"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any], persistence_type: str = PERSISTENCE_TYPE) -> str:
    normalized = _normalize_payload(payload, persistence_type=persistence_type)

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


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        return dict(default)

    return payload


def _default_registry() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_child_core_registry",
            "artifact_version": REGISTRY_VERSION,
            "registry_id": "PM_CORE_CHILD_CORE_REGISTRY",
            "status": "active",
            "updated_at": _utc_now(),
            "entries": {},
        }
    )


def _default_mirror_registry() -> Dict[str, Any]:
    payload = _default_registry()
    payload["artifact_type"] = "pm_child_core_registry_mirror"
    payload["persistence_type"] = "pm_child_core_registry_mirror"
    return payload


def load_registry() -> Dict[str, Any]:
    payload = _read_json(AUTHORITATIVE_REGISTRY_PATH, _default_registry())
    payload.setdefault("entries", {})
    return _normalize_payload(payload)


def save_registry(registry: Dict[str, Any]) -> str:
    normalized = _normalize_payload(registry)
    normalized["updated_at"] = _utc_now()
    normalized.setdefault("entries", {})
    return _governed_write(AUTHORITATIVE_REGISTRY_PATH, normalized)


def save_mirror_registry(registry: Dict[str, Any]) -> str:
    normalized = _normalize_payload(registry, persistence_type="pm_child_core_registry_mirror")
    normalized["artifact_type"] = "pm_child_core_registry_mirror"
    normalized["updated_at"] = _utc_now()
    normalized.setdefault("entries", {})
    return _governed_write(
        MIRROR_REGISTRY_PATH,
        normalized,
        persistence_type="pm_child_core_registry_mirror",
    )


def sync_mirror_registry() -> str:
    registry = load_registry()
    return save_mirror_registry(registry)


def get_entry(core_id: str) -> Optional[Dict[str, Any]]:
    clean_id = _safe_str(core_id)
    if not clean_id:
        return None

    entry = load_registry().get("entries", {}).get(clean_id)

    return dict(entry) if isinstance(entry, dict) else None


def validate_registered_core(core_id: str) -> Dict[str, Any]:
    clean_id = _safe_str(core_id)
    core_path = CHILD_CORES_DIR / clean_id

    missing_directories = [
        directory
        for directory in REQUIRED_DIRECTORIES
        if not (core_path / directory).exists()
    ]

    missing_files = [
        filename
        for filename in REQUIRED_FILES
        if not (core_path / filename).exists()
    ]

    valid = not missing_directories and not missing_files

    return {
        "artifact_type": "pm_child_core_validation",
        "artifact_version": REGISTRY_VERSION,
        "core_id": clean_id,
        "core_path": str(core_path),
        "valid": valid,
        "required_files_verified": valid,
        "structural_validation": "passed" if valid else "failed",
        "semantic_validation": "passed" if valid else "not_checked",
        "missing_directories": missing_directories,
        "missing_files": missing_files,
        "persistence_type": "pm_child_core_validation",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }


def register_core_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("entry must be a dict")

    core_id = _safe_str(entry.get("core_id"))
    if not core_id:
        raise ValueError("core_id is required")

    registry = load_registry()
    entries = _safe_dict(registry.get("entries"))

    normalized_entry = dict(entry)
    normalized_entry.setdefault("status", "validated")
    normalized_entry.setdefault("registered_at", _utc_now())
    normalized_entry["updated_at"] = _utc_now()
    normalized_entry["persistence_type"] = "pm_child_core_registry_entry"
    normalized_entry["mutation_class"] = MUTATION_CLASS
    normalized_entry["advisory_only"] = True
    normalized_entry["authority_metadata"] = dict(AUTHORITY_METADATA)

    entries[core_id] = normalized_entry
    registry["entries"] = entries

    save_registry(registry)
    sync_mirror_registry()

    return normalized_entry


def update_core_entry(core_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    clean_id = _safe_str(core_id)
    if not clean_id:
        raise ValueError("core_id is required")

    registry = load_registry()
    entries = _safe_dict(registry.get("entries"))
    current = entries.get(clean_id)

    if not isinstance(current, dict):
        raise ValueError(f"Child core '{clean_id}' is not registered.")

    updated = dict(current)
    updated.update(dict(updates or {}))
    updated["updated_at"] = _utc_now()
    updated["persistence_type"] = "pm_child_core_registry_entry"
    updated["mutation_class"] = MUTATION_CLASS
    updated["advisory_only"] = True
    updated["authority_metadata"] = dict(AUTHORITY_METADATA)

    entries[clean_id] = updated
    registry["entries"] = entries

    save_registry(registry)
    sync_mirror_registry()

    return updated


def activate_core(core_id: str, activation_receipt_path: str) -> Dict[str, Any]:
    return update_core_entry(
        core_id,
        {
            "status": "active",
            "activation_receipt_path": _safe_str(activation_receipt_path),
            "activation_governance_note": "Activation recorded as PM registry memory, not autonomous execution.",
        },
    )


def retire_core(core_id: str, retirement_receipt_path: str, notes: Optional[str] = None) -> Dict[str, Any]:
    return update_core_entry(
        core_id,
        {
            "status": "retired",
            "retirement_receipt_path": _safe_str(retirement_receipt_path),
            "notes": notes,
            "retirement_governance_note": "Retirement recorded as PM registry memory, not autonomous execution.",
        },
    )


def list_registered_cores() -> Dict[str, Dict[str, Any]]:
    entries = load_registry().get("entries", {})
    return entries if isinstance(entries, dict) else {}


def ensure_registry_files_exist() -> None:
    if not AUTHORITATIVE_REGISTRY_PATH.exists():
        save_registry(_default_registry())

    if not MIRROR_REGISTRY_PATH.exists():
        save_mirror_registry(_default_mirror_registry())

    sync_mirror_registry()
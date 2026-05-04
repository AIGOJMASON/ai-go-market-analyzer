from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = PM_CORE_DIR / "state" / "current"
STRATEGY_REGISTRY_PATH = STATE_DIR / "pm_strategy_registry.json"

STRATEGY_REGISTRY_VERSION = "northstar_pm_strategy_registry_v1"
MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "pm_strategy_registry"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_route_directly": False,
    "can_activate_child_core": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_strategy_registry_memory_only",
}


STRATEGY_REGISTRY = {
    "layer": "PM_CORE",
    "implementation_layer": "PM_CORE/strategy",
    "modules": {
        "pm_strategy": "PM_CORE/strategy/pm_strategy.py",
        "strategy_registry": "PM_CORE/strategy/strategy_registry.py",
        "child_core_registry": "PM_CORE/child_core_management/child_core_registry.py",
    },
    "receives": [
        "pm_continuity_update",
        "pm_refinement_record",
        "strategic_interpretation_record",
    ],
    "emits": [
        "pm_decision_packet",
        "pm_strategy_receipt",
    ],
    "boundary_rules": [
        "no research authority",
        "no continuity mutation outside PM continuity layer",
        "no child-core activation",
        "no routing execution",
        "no canon mutation",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "pm_strategy_registry")
    normalized.setdefault("artifact_version", STRATEGY_REGISTRY_VERSION)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["routing_execution_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
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
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def build_strategy_registry() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_strategy_registry",
            "artifact_version": STRATEGY_REGISTRY_VERSION,
            "updated_at": _utc_now(),
            "registry": dict(STRATEGY_REGISTRY),
        }
    )


def persist_strategy_registry(registry_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = registry_payload if isinstance(registry_payload, dict) else build_strategy_registry()
    normalized = _normalize_payload(payload)
    normalized["updated_at"] = _utc_now()

    path = _governed_write(STRATEGY_REGISTRY_PATH, normalized)

    return {
        "status": "persisted",
        "path": path,
        "registry": normalized,
    }


def load_strategy_registry() -> Dict[str, Any]:
    return _normalize_payload(_read_json(STRATEGY_REGISTRY_PATH, build_strategy_registry()))
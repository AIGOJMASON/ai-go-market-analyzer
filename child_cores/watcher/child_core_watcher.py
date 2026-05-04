from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


WATCHER_VERSION = "northstar_child_core_watcher_v1"


# =========================
# Helpers
# =========================

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _state_root() -> Path:
    return state_root() / "child_core_watcher"


def _watcher_root() -> Path:
    return _state_root() / "records"


# =========================
# Governance Blocks
# =========================

def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "child_core_watcher_validation",
        "mutation_class": "child_core_watcher_persistence",
        "advisory_only": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "child_core_watcher",
        "advisory_only": True,
        "watcher_authority": True,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_execution_gate": False,
        "can_override_watcher": False,
        "can_write_outside_governed_persistence": False,
    }


# =========================
# Persistence
# =========================

def _persist_record(record: Dict[str, Any]) -> Path:
    request_id = _safe_str(record.get("request_id")) or "unknown"
    validation_id = _safe_str(record.get("validation_id")) or f"watcher_{request_id}"

    path = _watcher_root() / f"{validation_id}.json"

    governed_write_json(
        path=path,
        payload=record,
        mutation_class="child_core_watcher_persistence",
        persistence_type="child_core_watcher_validation",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_child_core_watcher_validation",
            "layer": "child_cores.watcher.child_core_watcher",
        },
    )

    return path


# =========================
# Validation Logic
# =========================

def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload_not_dict"]

    if not _safe_str(payload.get("request_id")):
        errors.append("missing_request_id")

    # Execution safety
    if payload.get("execution_allowed") is True:
        errors.append("execution_not_allowed")

    if payload.get("runtime_mutation_allowed") is True:
        errors.append("runtime_mutation_not_allowed")

    # Authority safety
    authority = _safe_dict(payload.get("authority"))
    if authority.get("can_execute") is True:
        errors.append("authority_execute_not_allowed")

    return sorted(set(errors))


# =========================
# Builder
# =========================

def build_watcher_validation(payload: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(payload)

    errors = _validate_payload(source)
    valid = len(errors) == 0

    request_id = _safe_str(source.get("request_id")) or "unknown"

    validation_id = (
        f"child_watcher_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{request_id}"
    )

    return {
        "artifact_type": "child_core_watcher_validation",
        "artifact_version": WATCHER_VERSION,
        "validation_id": validation_id,
        "checked_at": _utc_now_iso(),
        "request_id": request_id,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "errors": errors,
        "source_artifact": source,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


# =========================
# Public API
# =========================

def watch(payload: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
    validation = build_watcher_validation(payload)

    watcher_path = ""
    if persist:
        watcher_path = str(_persist_record(validation))

    return {
        "status": validation["status"],
        "valid": validation["valid"],
        "validation": validation,
        "validation_id": validation["validation_id"],
        "watcher_path": watcher_path,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def run_child_core_watcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    return watch(payload, persist=True)
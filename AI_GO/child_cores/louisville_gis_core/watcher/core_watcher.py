from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


CORE_WATCHER_VERSION = "northstar_louisville_gis_watcher_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _state_root() -> Path:
    return state_root() / "louisville_gis_core"


def _watcher_root() -> Path:
    return _state_root() / "watcher"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "louisville_gis_watcher_validation",
        "mutation_class": "louisville_gis_watcher_persistence",
        "advisory_only": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "louisville_gis_core_watcher",
        "advisory_only": True,
        "watcher_authority": True,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
    }


def _persist_watcher_record(record: Dict[str, Any]) -> Path:
    request_id = _safe_str(record.get("request_id")) or "unknown_request"
    validation_id = _safe_str(record.get("validation_id")) or f"watcher_{request_id}"
    path = _watcher_root() / f"{validation_id}.json"

    governed_write_json(
        path=path,
        payload=record,
        mutation_class="louisville_gis_watcher_persistence",
        persistence_type="louisville_gis_watcher_validation",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_louisville_gis_watcher_validation",
            "child_core_id": "louisville_gis_core",
            "layer": "watcher.core_watcher",
        },
    )

    return path


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload_not_dict"]

    if not _safe_str(payload.get("request_id")):
        errors.append("missing_request_id")

    if payload.get("execution_allowed") is True:
        errors.append("execution_allowed_must_not_be_true")

    if payload.get("runtime_mutation_allowed") is True:
        errors.append("runtime_mutation_allowed_must_not_be_true")

    authority = _safe_dict(payload.get("authority"))
    if authority.get("can_execute") is True:
        errors.append("authority_can_execute_must_not_be_true")

    return sorted(set(errors))


def build_watcher_validation(payload: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(payload)
    errors = _validate_payload(source)
    valid = len(errors) == 0

    request_id = _safe_str(source.get("request_id")) or "unknown_request"
    validation_id = f"gis_watcher_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{request_id}"

    return {
        "artifact_type": "louisville_gis_watcher_validation",
        "artifact_version": CORE_WATCHER_VERSION,
        "validation_id": validation_id,
        "checked_at": _utc_now_iso(),
        "child_core_id": "louisville_gis_core",
        "request_id": request_id,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "errors": errors,
        "source_artifact": source,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def watch(payload: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
    validation = build_watcher_validation(payload)

    watcher_path = ""
    if persist:
        watcher_path = str(_persist_watcher_record(validation))

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


def run_core_watcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    return watch(payload, persist=True)
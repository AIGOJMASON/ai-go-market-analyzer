from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


OUTPUT_BUILDER_VERSION = "northstar_louisville_gis_output_v1"


class LouisvilleGISOutputError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _state_root() -> Path:
    return state_root() / "louisville_gis_core"


def _output_root() -> Path:
    return _state_root() / "outputs"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "louisville_gis_output_record",
        "mutation_class": "louisville_gis_output_persistence",
        "advisory_only": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "louisville_gis_core_output_builder",
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
    }


def _persist_output_record(record: Dict[str, Any]) -> Path:
    request_id = _safe_str(record.get("request_id")) or "unknown_request"
    output_id = _safe_str(record.get("output_id")) or f"output_{request_id}"
    path = _output_root() / f"{output_id}.json"

    governed_write_json(
        path=path,
        payload=record,
        mutation_class="louisville_gis_output_persistence",
        persistence_type="louisville_gis_output_record",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_louisville_gis_output_record",
            "child_core_id": "louisville_gis_core",
            "layer": "outputs.output_builder",
        },
    )

    return path


def build_output_record(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(runtime_result, dict):
        raise LouisvilleGISOutputError("runtime_result must be a dict")

    request_id = _safe_str(runtime_result.get("request_id"))
    if not request_id:
        raise LouisvilleGISOutputError("request_id is required")

    output_id = _safe_str(runtime_result.get("output_id")) or f"gis_output_{request_id}"

    return {
        "artifact_type": "louisville_gis_output_record",
        "artifact_version": OUTPUT_BUILDER_VERSION,
        "status": _safe_str(runtime_result.get("status")) or "ok",
        "output_id": output_id,
        "request_id": request_id,
        "created_at": _utc_now_iso(),
        "child_core_id": "louisville_gis_core",
        "summary": _safe_str(runtime_result.get("summary")),
        "views": _safe_dict(runtime_result.get("views")),
        "results": _safe_list(runtime_result.get("results")),
        "source_runtime_result": deepcopy(runtime_result),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def build_output(runtime_result: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
    record = build_output_record(runtime_result)

    output_path = ""
    if persist:
        output_path = str(_persist_output_record(record))

    return {
        "status": "built",
        "request_id": record["request_id"],
        "output_id": record["output_id"],
        "output_record": record,
        "output_path": output_path,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def run_output_builder(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    return build_output(runtime_result, persist=True)

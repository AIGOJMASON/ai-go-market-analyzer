from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_append_jsonl, governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


CORE_SMI_VERSION = "northstar_louisville_gis_smi_v1"


class LouisvilleGISSmiError(ValueError):
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


def _smi_root() -> Path:
    return _state_root() / "smi"


def _latest_path() -> Path:
    return _smi_root() / "latest_core_smi_record.json"


def _history_path() -> Path:
    return _smi_root() / "core_smi_history.jsonl"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "louisville_gis_smi_record",
        "mutation_class": "louisville_gis_smi_persistence",
        "advisory_only": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "louisville_gis_core_smi",
        "advisory_only": True,
        "continuity_authority": True,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
    }


def _persist_smi_record(record: Dict[str, Any]) -> Dict[str, str]:
    governed_write_json(
        path=_latest_path(),
        payload=record,
        mutation_class="louisville_gis_smi_persistence",
        persistence_type="louisville_gis_smi_latest_record",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_louisville_gis_latest_smi_record",
            "child_core_id": "louisville_gis_core",
            "layer": "smi.core_smi",
        },
    )

    governed_append_jsonl(
        path=_history_path(),
        payload=record,
        mutation_class="louisville_gis_smi_persistence",
        persistence_type="louisville_gis_smi_history_record",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "append_louisville_gis_smi_history_record",
            "child_core_id": "louisville_gis_core",
            "layer": "smi.core_smi",
        },
    )

    return {
        "latest_path": str(_latest_path()),
        "history_path": str(_history_path()),
    }


def build_core_smi_record(
    *,
    event_type: str,
    request_id: str = "",
    source_artifact: Dict[str, Any] | None = None,
    notes: str = "",
) -> Dict[str, Any]:
    clean_event_type = _safe_str(event_type)
    if not clean_event_type:
        raise LouisvilleGISSmiError("event_type is required")

    source = _safe_dict(source_artifact)

    clean_request_id = _safe_str(request_id) or _safe_str(source.get("request_id"))
    record_id = f"gis_smi_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{clean_event_type}"

    return {
        "artifact_type": "louisville_gis_core_smi_record",
        "artifact_version": CORE_SMI_VERSION,
        "record_id": record_id,
        "recorded_at": _utc_now_iso(),
        "child_core_id": "louisville_gis_core",
        "event_type": clean_event_type,
        "request_id": clean_request_id,
        "notes": _safe_str(notes),
        "source_artifact_type": _safe_str(source.get("artifact_type")),
        "source_status": _safe_str(source.get("status")),
        "source_artifact": source,
        "continuity": {
            "request_id": clean_request_id,
            "event_type": clean_event_type,
            "source_refs": _safe_list(source.get("source_refs")),
        },
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def record_core_smi(
    *,
    event_type: str,
    request_id: str = "",
    source_artifact: Dict[str, Any] | None = None,
    notes: str = "",
) -> Dict[str, Any]:
    record = build_core_smi_record(
        event_type=event_type,
        request_id=request_id,
        source_artifact=source_artifact,
        notes=notes,
    )
    paths = _persist_smi_record(record)

    return {
        "status": "recorded",
        "record": record,
        "record_id": record["record_id"],
        **paths,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def run_core_smi(source_artifact: Dict[str, Any]) -> Dict[str, Any]:
    return record_core_smi(
        event_type=_safe_str(source_artifact.get("artifact_type")) or "gis_core_event",
        request_id=_safe_str(source_artifact.get("request_id")),
        source_artifact=source_artifact,
    )
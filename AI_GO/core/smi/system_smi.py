from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


SYSTEM_SMI_VERSION = "v1.0"
MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "system_smi_record"

STATE_ROOT = state_root() / "system_smi"
LATEST_PATH = STATE_ROOT / "latest_system_smi_record.json"
HISTORY_PATH = STATE_ROOT / "system_smi_history.jsonl"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "system_smi_awareness_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)

    authority = dict(normalized.get("authority", {}))
    authority["can_execute"] = False
    authority["can_mutate_source_artifacts"] = False
    authority["can_override_governance"] = False
    authority["can_override_watcher"] = False
    authority["can_write_external_memory"] = False
    normalized["authority"] = authority

    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
    normalized = _normalize_record(payload)

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


def build_system_smi_record(
    *,
    source_packet: dict[str, Any],
    event_type: str = "root_intelligence_spine_run",
) -> dict[str, Any]:
    packet = _safe_dict(source_packet)
    research = _safe_dict(packet.get("research_packet"))
    handoff = _safe_dict(packet.get("engine_handoff_packet"))
    continuity_packet = _safe_dict(handoff.get("child_core_handoff"))
    child_packet = _safe_dict(continuity_packet.get("packet"))
    curation = _safe_dict(handoff.get("curation"))

    record_id = (
        "smi_system_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid4().hex[:10]}"
    )

    return _normalize_record(
        {
            "artifact_type": "system_smi_record",
            "artifact_version": SYSTEM_SMI_VERSION,
            "record_id": record_id,
            "recorded_at": _utc_now_iso(),
            "event_type": event_type,
            "sealed": True,
            "authority": {
                "authority_id": "SMI",
                "system_wide": True,
                "continuity_authority": True,
                "connects_to_system_brain": True,
                "can_execute": False,
                "can_mutate_source_artifacts": False,
                "can_override_governance": False,
                "can_override_watcher": False,
                "can_write_external_memory": False,
            },
            "continuity": {
                "source_artifact_type": packet.get("artifact_type"),
                "source_trace_id": packet.get("trace_id"),
                "research_packet_id": research.get("packet_id"),
                "handoff_allowed": continuity_packet.get("allowed"),
                "target_child_core_id": child_packet.get("target_child_core_id"),
                "curation_status": curation.get("status"),
                "child_core_id": _safe_str(child_packet.get("target_child_core_id")),
                "project_id": _safe_str(_safe_dict(research.get("input")).get("project_id")),
                "phase_id": _safe_str(_safe_dict(research.get("input")).get("phase_id")),
            },
            "system_brain_signal": {
                "available": True,
                "summary": "Root intelligence spine event recorded into system-wide SMI continuity.",
                "posture": "advisory_continuity_only",
            },
            "use_policy": {
                "may_be_read_by_system_brain": True,
                "may_be_read_by_operator_surface": True,
                "may_be_read_by_pm": True,
                "may_execute": False,
                "may_mutate_state": False,
                "may_override_governance": False,
            },
        }
    )


def load_latest_system_smi_record() -> dict[str, Any]:
    return _read_json(LATEST_PATH, {})


def persist_system_smi_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_record(record)

    latest_result = _governed_write(LATEST_PATH, normalized)

    history_record = dict(normalized)
    existing_history = _read_json(
        HISTORY_PATH,
        {
            "artifact_type": "system_smi_history",
            "artifact_version": SYSTEM_SMI_VERSION,
            "persistence_type": "system_smi_history",
            "mutation_class": MUTATION_CLASS,
            "advisory_only": True,
            "authority_metadata": dict(AUTHORITY_METADATA),
            "records": [],
        },
    )

    records = existing_history.get("records", [])
    if not isinstance(records, list):
        records = []

    records.append(history_record)
    existing_history["records"] = records[-1000:]
    existing_history["updated_at"] = _utc_now_iso()

    history_result = _governed_write(HISTORY_PATH, existing_history)

    return {
        "status": "persisted",
        "record_id": normalized.get("record_id"),
        "latest_path": str(
            latest_result.get("path")
            if isinstance(latest_result, dict) and latest_result.get("path")
            else LATEST_PATH
        ),
        "history_path": str(
            history_result.get("path")
            if isinstance(history_result, dict) and history_result.get("path")
            else HISTORY_PATH
        ),
        "record": normalized,
    }
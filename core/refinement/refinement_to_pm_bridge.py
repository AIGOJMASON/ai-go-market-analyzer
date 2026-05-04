from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "state" / "refinement" / "current" / "continuity_weighting_refinement_packet.json"
OUTPUT_PATH = PROJECT_ROOT / "state" / "pm_refinement" / "current" / "pm_refinement_intake_record.json"

MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "pm_refinement_intake_record"


AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_workflow_state": False,
    "can_mutate_project_truth": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_refinement_awareness_only",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        return default

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return default


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return dict(AUTHORITY_METADATA)


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    normalized["artifact_type"] = "pm_refinement_intake_record"
    normalized["artifact_version"] = "northstar_pm_refinement_bridge_v1"
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["annotation_only"] = True
    normalized["classification"] = _classification_block()
    normalized["authority"] = _authority_block()
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
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
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _default_refinement_packet() -> Dict[str, Any]:
    return {
        "packet_id": "continuity_weighting_refinement_default",
        "timestamp": None,
        "source_record_path": "state/continuity_weighting/current/continuity_weighting_record.json",
        "annotation_only": True,
        "top_pattern_key": None,
        "top_pattern_status": None,
        "top_pattern_weight": 0.0,
        "recurrence_count": 0,
        "source_surface": None,
        "event_class": None,
        "symbol": None,
        "event_theme": None,
        "signal_class": "low_signal",
        "confidence_posture": "none",
        "advisory_note": "No continuity pattern available",
    }


def build_pm_refinement_intake_record() -> Dict[str, Any]:
    packet = _read_json(INPUT_PATH, _default_refinement_packet())

    record = {
        "record_id": f"pm_refinement_intake_{utc_now_iso().replace(':', '-')}",
        "timestamp": utc_now_iso(),
        "source_packet_path": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "source_packet_id": packet.get("packet_id"),
        "annotation_only": bool(packet.get("annotation_only", True)),
        "pm_surface": "refinement_intake",
        "source_surface": packet.get("source_surface"),
        "top_pattern_key": packet.get("top_pattern_key"),
        "top_pattern_status": packet.get("top_pattern_status"),
        "top_pattern_weight": packet.get("top_pattern_weight"),
        "recurrence_count": packet.get("recurrence_count"),
        "confidence_posture": packet.get("confidence_posture"),
        "advisory_note": packet.get("advisory_note"),
        "event_class": packet.get("event_class"),
        "symbol": packet.get("symbol"),
        "event_theme": packet.get("event_theme"),
        "signal_class": packet.get("signal_class"),
    }

    return _normalize_record(record)


def generate_and_persist_pm_refinement_intake_record() -> Dict[str, Any]:
    record = build_pm_refinement_intake_record()
    record["path"] = _governed_write(OUTPUT_PATH, record)
    return record
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "state" / "refinement" / "current" / "outcome_feedback_refinement_packet.json"
OUTPUT_PATH = PROJECT_ROOT / "state" / "pm_refinement" / "current" / "outcome_refinement_intake_record.json"

MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "outcome_refinement_pm_intake_record"


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
    "authority_scope": "outcome_refinement_pm_awareness_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        return default

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
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
    normalized["artifact_type"] = "outcome_refinement_pm_intake_record"
    normalized["artifact_version"] = "northstar_outcome_refinement_to_pm_bridge_v1"
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


def _default_packet() -> Dict[str, Any]:
    return {
        "packet_id": "outcome_feedback_refinement_default",
        "timestamp": None,
        "annotation_only": True,
        "refinement_signal": {},
    }


def build_outcome_refinement_pm_intake_record() -> Dict[str, Any]:
    packet = _read_json(INPUT_PATH, _default_packet())
    refinement_signal = packet.get("refinement_signal")
    if not isinstance(refinement_signal, dict):
        refinement_signal = {}

    record = {
        "record_id": f"outcome_refinement_pm_intake_{_utc_now_iso().replace(':', '-')}",
        "timestamp": _utc_now_iso(),
        "source_packet_path": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "source_packet_id": packet.get("packet_id"),
        "annotation_only": bool(packet.get("annotation_only", True)),
        "pm_surface": "outcome_refinement_intake",
        "closeout_id": packet.get("closeout_id"),
        "core_id": packet.get("core_id"),
        "outcome_class": packet.get("outcome_class"),
        "confidence_delta": packet.get("confidence_delta"),
        "refinement_posture": refinement_signal.get("refinement_posture"),
        "outcome_feedback_available": refinement_signal.get("outcome_feedback_available", False),
        "advisory_note": "Outcome refinement forwarded to PM awareness without authority mutation.",
    }

    return _normalize_record(record)


def generate_and_persist_outcome_refinement_pm_intake_record() -> Dict[str, Any]:
    record = build_outcome_refinement_pm_intake_record()
    record["path"] = _governed_write(OUTPUT_PATH, record)
    return record
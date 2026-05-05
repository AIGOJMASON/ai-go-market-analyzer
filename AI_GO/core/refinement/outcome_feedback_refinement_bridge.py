from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "state" / "refinement" / "current" / "outcome_feedback_refinement_packet.json"

MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "outcome_feedback_refinement_packet"


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
    "authority_scope": "outcome_feedback_refinement_awareness_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


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


def _normalize_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(packet)
    normalized["artifact_type"] = "outcome_feedback_refinement_packet"
    normalized["artifact_version"] = "northstar_outcome_feedback_refinement_bridge_v1"
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["annotation_only"] = True
    normalized["classification"] = _classification_block()
    normalized["authority"] = _authority_block()
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_packet(payload)

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


def build_outcome_feedback_refinement_packet(
    *,
    outcome_feedback_record: Dict[str, Any],
    source: str = "outcome_feedback",
) -> Dict[str, Any]:
    record = outcome_feedback_record if isinstance(outcome_feedback_record, dict) else {}

    packet = {
        "packet_id": f"outcome_feedback_refinement_{_utc_now_iso().replace(':', '-')}",
        "timestamp": _utc_now_iso(),
        "source": _safe_str(source) or "outcome_feedback",
        "source_record_id": record.get("record_id"),
        "closeout_id": record.get("closeout_id"),
        "core_id": record.get("core_id"),
        "outcome_class": record.get("outcome_class"),
        "confidence_delta": record.get("confidence_delta"),
        "expected_behavior": record.get("expected_behavior"),
        "actual_outcome": record.get("actual_outcome"),
        "refinement_signal": {
            "refinement_posture": "observe",
            "outcome_feedback_available": True,
            "confidence_delta": record.get("confidence_delta"),
            "outcome_class": record.get("outcome_class"),
        },
    }

    return _normalize_packet(packet)


def persist_outcome_feedback_refinement_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _normalize_packet(packet)
    normalized["path"] = _governed_write(OUTPUT_PATH, normalized)
    return normalized


def generate_and_persist_outcome_feedback_refinement_packet(
    *,
    outcome_feedback_record: Dict[str, Any],
    source: str = "outcome_feedback",
) -> Dict[str, Any]:
    packet = build_outcome_feedback_refinement_packet(
        outcome_feedback_record=outcome_feedback_record,
        source=source,
    )
    return persist_outcome_feedback_refinement_packet(packet)
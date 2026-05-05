from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.visibility.correctness_visibility_policy import (
    normalize_history_view,
    validate_outcome_feedback_record,
    validate_pm_intake_record,
    validate_refinement_packet,
)


MUTATION_CLASS = "visibility_persistence"
PERSISTENCE_TYPE = "correctness_visibility"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "correctness_visibility_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _state_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "state"
        / "system_visibility"
        / "CORRECTNESS_VISIBILITY.latest.json"
    )


def _normalize_artifact(artifact: dict) -> dict:
    normalized = dict(artifact)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_influence"] = False
    normalized["runtime_mutation_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: dict) -> Any:
    normalized = _normalize_artifact(payload)

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


def _persist_visibility_artifact(artifact: dict) -> None:
    _governed_write(_state_path(), artifact)


def build_correctness_visibility_artifact(
    *,
    outcome_feedback_record: dict,
    outcome_feedback_index: dict,
    refinement_packet: dict,
    pm_intake_record: dict,
    core_id: str,
) -> dict:
    if not core_id:
        return {
            "status": "rejected",
            "reason": "missing_core_id",
        }

    try:
        validate_outcome_feedback_record(outcome_feedback_record)
    except ValueError as exc:
        return {
            "status": "rejected",
            "reason": str(exc),
        }

    try:
        validate_refinement_packet(refinement_packet)
    except ValueError as exc:
        return {
            "status": "rejected",
            "reason": str(exc),
        }

    try:
        validate_pm_intake_record(pm_intake_record)
    except ValueError as exc:
        return {
            "status": "rejected",
            "reason": str(exc),
        }

    refinement_signal = refinement_packet.get("refinement_signal", {})
    pm_signal = pm_intake_record.get("pm_signal", {})
    history_view = normalize_history_view(outcome_feedback_index)

    artifact = _normalize_artifact(
        {
            "artifact_type": "correctness_visibility",
            "artifact_version": "v1",
            "generated_at": _utc_now(),
            "status": "generated",
            "annotation_only": True,
            "visibility_only": True,
            "core_id": core_id,
            "correctness_summary": {
                "latest_outcome_class": outcome_feedback_record.get("outcome_class"),
                "latest_confidence_delta": outcome_feedback_record.get("confidence_delta"),
                "refinement_posture": refinement_signal.get("refinement_posture"),
                "pm_awareness_posture": pm_signal.get("pm_awareness_posture"),
                "entry_count": history_view.get("entry_count"),
            },
            "outcome_view": {
                "closeout_id": outcome_feedback_record.get("closeout_id"),
                "recorded_at": outcome_feedback_record.get("recorded_at"),
                "expected_behavior": outcome_feedback_record.get("expected_behavior"),
                "actual_outcome": outcome_feedback_record.get("actual_outcome"),
                "outcome_class": outcome_feedback_record.get("outcome_class"),
                "confidence_delta": outcome_feedback_record.get("confidence_delta"),
            },
            "refinement_view": refinement_signal,
            "pm_awareness_view": pm_signal,
            "history_view": history_view,
        }
    )

    _persist_visibility_artifact(artifact)
    return artifact
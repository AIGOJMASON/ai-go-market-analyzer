
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


OUTCOME_FEEDBACK_RECORD_VERSION = "northstar_outcome_feedback_record_v1"
STATE_ROOT = state_root() / "outcome_feedback"
MUTATION_CLASS = "outcome_persistence"
PERSISTENCE_TYPE = "outcome_feedback_record"


AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_operational_state": False,
    "can_mutate_workflow_state": False,
    "can_mutate_project_truth": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "can_override_state_authority": False,
    "can_override_cross_core_integrity": False,
    "authority_scope": "outcome_feedback_record_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return dict(AUTHORITY_METADATA)


def get_outcome_feedback_record_path() -> Path:
    return STATE_ROOT / "current" / "outcome_feedback_record.json"


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    normalized["artifact_type"] = "outcome_feedback_record"
    normalized["artifact_version"] = OUTCOME_FEEDBACK_RECORD_VERSION
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["classification"] = _classification_block()
    normalized["authority"] = _authority_block()
    normalized["execution_influence"] = False
    normalized["runtime_mutation_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
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


def build_outcome_feedback_record(
    *,
    closeout_id: str,
    expected_behavior: str,
    actual_outcome: str,
    outcome_class: str,
    confidence_delta: str,
    core_id: str = "market_analyzer_v1",
    observed_outcome_view: Dict[str, Any] | None = None,
    source: str = "outcome_feedback",
    notes: str = "",
) -> Dict[str, Any]:
    record_id = (
        f"outcome_feedback_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid4().hex[:10]}"
    )

    return _normalize_record(
        {
            "record_id": record_id,
            "recorded_at": _utc_now_iso(),
            "closeout_id": _safe_str(closeout_id),
            "core_id": _safe_str(core_id) or "market_analyzer_v1",
            "source": _safe_str(source) or "outcome_feedback",
            "expected_behavior": _safe_str(expected_behavior),
            "actual_outcome": _safe_str(actual_outcome),
            "outcome_class": _safe_str(outcome_class),
            "confidence_delta": _safe_str(confidence_delta),
            "observed_outcome_view": _safe_dict(observed_outcome_view),
            "notes": _safe_str(notes),
        }
    )


def validate_outcome_feedback_record(record: Dict[str, Any]) -> list[str]:
    errors: list[str] = []
    payload = _safe_dict(record)

    for field_name in [
        "record_id",
        "recorded_at",
        "closeout_id",
        "core_id",
        "expected_behavior",
        "actual_outcome",
        "outcome_class",
        "confidence_delta",
    ]:
        if not _safe_str(payload.get(field_name)):
            errors.append(f"missing_required_field:{field_name}")

    if payload.get("mutation_class") not in {None, MUTATION_CLASS}:
        errors.append("invalid_mutation_class")

    if payload.get("advisory_only") not in {None, True}:
        errors.append("outcome_feedback_must_be_advisory_only")

    return errors


def write_outcome_feedback_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _normalize_record(record)
    errors = validate_outcome_feedback_record(normalized)

    if errors:
        return {
            "status": "rejected",
            "errors": errors,
            "record": normalized,
        }

    path = get_outcome_feedback_record_path()
    written_path = _governed_write(path, normalized)

    return {
        "status": "persisted",
        "artifact_type": "outcome_feedback_record_write",
        "record_id": normalized.get("record_id"),
        "path": written_path,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "record": normalized,
    }


def read_outcome_feedback_record() -> Dict[str, Any]:
    path = get_outcome_feedback_record_path()

    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("outcome feedback record must be a JSON object")

    return payload


def create_and_write_outcome_feedback_record(**kwargs: Any) -> Dict[str, Any]:
    record = build_outcome_feedback_record(**kwargs)
    return write_outcome_feedback_record(record)


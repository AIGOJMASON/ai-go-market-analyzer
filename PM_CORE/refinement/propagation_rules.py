from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = PM_CORE_DIR / "state" / "current"
PROPAGATION_STATE_PATH = STATE_DIR / "pm_refinement_propagation_state.json"

PROPAGATION_VERSION = "northstar_pm_refinement_propagation_v1"
MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "pm_refinement_propagation_state"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_workflow_state": False,
    "can_mutate_pm_authority": False,
    "can_override_refinement_arbitrator": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_refinement_propagation_awareness_only",
}


APPROVED_PROPAGATION_ACTIONS = {
    "hold",
    "pass_to_pm",
    "condition_for_child_core",
    "escalate_for_review",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "pm_refinement_propagation_state")
    normalized.setdefault("artifact_version", PROPAGATION_VERSION)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    normalized["runtime_mutation_allowed"] = False
    normalized.setdefault("records", [])
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_payload(payload)

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
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _default_state() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_refinement_propagation_state",
            "artifact_version": PROPAGATION_VERSION,
            "updated_at": _utc_now(),
            "records": [],
        }
    )


def determine_propagation_action(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    record = refinement_record if isinstance(refinement_record, dict) else {}
    posture = str(
        record.get("confidence_posture")
        or record.get("refinement_posture")
        or record.get("signal_class")
        or ""
    ).strip()

    if posture in {"strong_attention", "dominant_pattern"}:
        action = "escalate_for_review"
    elif posture in {"elevated_attention", "active_pattern"}:
        action = "pass_to_pm"
    elif posture in {"slight_attention", "emerging_pattern"}:
        action = "condition_for_child_core"
    else:
        action = "hold"

    return {
        "artifact_type": "pm_refinement_propagation_decision",
        "artifact_version": PROPAGATION_VERSION,
        "action": action,
        "allowed_actions": sorted(APPROVED_PROPAGATION_ACTIONS),
        "reason": f"bounded_posture:{posture or 'none'}",
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_workflow_state": False,
    }


def record_propagation_decision(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    state = _normalize_payload(_read_json(PROPAGATION_STATE_PATH, _default_state()))
    records = state.get("records", [])
    if not isinstance(records, list):
        records = []

    decision = determine_propagation_action(refinement_record)
    entry = {
        "artifact_type": "pm_refinement_propagation_record",
        "artifact_version": PROPAGATION_VERSION,
        "recorded_at": _utc_now(),
        "source_record_id": refinement_record.get("record_id") if isinstance(refinement_record, dict) else None,
        "source_packet_id": refinement_record.get("packet_id") if isinstance(refinement_record, dict) else None,
        "decision": decision,
        "persistence_type": "pm_refinement_propagation_record",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    records.append(entry)
    state["records"] = records[-1000:]
    state["updated_at"] = _utc_now()

    path = _governed_write(PROPAGATION_STATE_PATH, state)

    return {
        "status": "recorded",
        "path": path,
        "entry": entry,
    }


def propagate_refinement_record(refinement_record: Dict[str, Any]) -> Dict[str, Any]:
    return record_propagation_decision(refinement_record)
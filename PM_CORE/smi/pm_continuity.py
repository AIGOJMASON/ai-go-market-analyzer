from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = PM_CORE_DIR / "state" / "current"

PM_CONTINUITY_STATE_PATH = STATE_DIR / "pm_continuity_state.json"
PM_CHANGE_LEDGER_PATH = STATE_DIR / "pm_change_ledger.json"
PM_UNRESOLVED_QUEUE_PATH = STATE_DIR / "pm_unresolved_queue.json"

PM_CONTINUITY_VERSION = "northstar_pm_continuity_v1"
MUTATION_CLASS = "memory_persistence"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_activate_child_core": False,
    "can_auto_route_work": False,
    "can_mutate_workflow_state": False,
    "can_reclassify_research_truth": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_decision_memory_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(payload: Dict[str, Any], persistence_type: str) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_version", PM_CONTINUITY_VERSION)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
    normalized["routing_execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any], persistence_type: str) -> str:
    normalized = _normalize_payload(payload, persistence_type)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
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
            "artifact_type": "pm_continuity_state",
            "artifact_version": PM_CONTINUITY_VERSION,
            "updated_at": _utc_now(),
            "total_updates": 0,
            "latest_update_id": "",
            "child_core_counts": {},
            "action_counts": {},
            "recent_references": [],
        },
        "pm_continuity_state",
    )


def _default_ledger() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_change_ledger",
            "artifact_version": PM_CONTINUITY_VERSION,
            "updated_at": _utc_now(),
            "entries": [],
        },
        "pm_change_ledger",
    )


def _default_unresolved_queue() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_unresolved_queue",
            "artifact_version": PM_CONTINUITY_VERSION,
            "updated_at": _utc_now(),
            "items": [],
        },
        "pm_unresolved_queue",
    )


def load_pm_continuity_state() -> Dict[str, Any]:
    return _normalize_payload(
        _read_json(PM_CONTINUITY_STATE_PATH, _default_state()),
        "pm_continuity_state",
    )


def load_pm_change_ledger() -> Dict[str, Any]:
    return _normalize_payload(
        _read_json(PM_CHANGE_LEDGER_PATH, _default_ledger()),
        "pm_change_ledger",
    )


def load_pm_unresolved_queue() -> Dict[str, Any]:
    return _normalize_payload(
        _read_json(PM_UNRESOLVED_QUEUE_PATH, _default_unresolved_queue()),
        "pm_unresolved_queue",
    )


def _extract_reference(source_record: Dict[str, Any]) -> Dict[str, Any]:
    record = source_record if isinstance(source_record, dict) else {}

    return {
        "source_record_id": record.get("record_id") or record.get("packet_id"),
        "source_artifact_type": record.get("artifact_type"),
        "target_child_core_id": record.get("target_child_core_id") or record.get("child_core_id"),
        "recommended_action": record.get("recommended_action") or record.get("action"),
        "summary": record.get("summary") or record.get("advisory_note") or "",
    }


def update_pm_continuity(source_record: Dict[str, Any]) -> Dict[str, Any]:
    state = load_pm_continuity_state()
    ledger = load_pm_change_ledger()
    unresolved = load_pm_unresolved_queue()

    update_id = f"pm_continuity_update_{_utc_now().replace(':', '-')}"
    reference = _extract_reference(source_record)

    child_core = str(reference.get("target_child_core_id") or "unknown")
    action = str(reference.get("recommended_action") or "unknown")

    child_counts = state.get("child_core_counts", {})
    if not isinstance(child_counts, dict):
        child_counts = {}
    child_counts[child_core] = int(child_counts.get(child_core, 0) or 0) + 1

    action_counts = state.get("action_counts", {})
    if not isinstance(action_counts, dict):
        action_counts = {}
    action_counts[action] = int(action_counts.get(action, 0) or 0) + 1

    recent = state.get("recent_references", [])
    if not isinstance(recent, list):
        recent = []
    recent.append(reference)

    state["updated_at"] = _utc_now()
    state["total_updates"] = int(state.get("total_updates", 0) or 0) + 1
    state["latest_update_id"] = update_id
    state["child_core_counts"] = child_counts
    state["action_counts"] = action_counts
    state["recent_references"] = recent[-50:]

    ledger_entries = ledger.get("entries", [])
    if not isinstance(ledger_entries, list):
        ledger_entries = []

    ledger_entry = {
        "artifact_type": "pm_change_ledger_entry",
        "artifact_version": PM_CONTINUITY_VERSION,
        "update_id": update_id,
        "recorded_at": _utc_now(),
        "reference": reference,
        "persistence_type": "pm_change_ledger_entry",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    ledger_entries.append(ledger_entry)
    ledger["entries"] = ledger_entries[-1000:]
    ledger["updated_at"] = _utc_now()

    unresolved_items = unresolved.get("items", [])
    if not isinstance(unresolved_items, list):
        unresolved_items = []

    if action in {"hold", "unknown", "escalate_for_review"}:
        unresolved_items.append(
            {
                "artifact_type": "pm_unresolved_queue_item",
                "artifact_version": PM_CONTINUITY_VERSION,
                "update_id": update_id,
                "created_at": _utc_now(),
                "reason": f"pm_action_requires_followup:{action}",
                "reference": reference,
                "persistence_type": "pm_unresolved_queue_item",
                "mutation_class": MUTATION_CLASS,
                "advisory_only": True,
                "authority_metadata": dict(AUTHORITY_METADATA),
            }
        )

    unresolved["items"] = unresolved_items[-500:]
    unresolved["updated_at"] = _utc_now()

    state_path = _governed_write(PM_CONTINUITY_STATE_PATH, state, "pm_continuity_state")
    ledger_path = _governed_write(PM_CHANGE_LEDGER_PATH, ledger, "pm_change_ledger")
    unresolved_path = _governed_write(PM_UNRESOLVED_QUEUE_PATH, unresolved, "pm_unresolved_queue")

    return {
        "status": "updated",
        "update_id": update_id,
        "state_path": state_path,
        "ledger_path": ledger_path,
        "unresolved_queue_path": unresolved_path,
        "state": state,
    }


def record_pm_continuity(source_record: Dict[str, Any]) -> Dict[str, Any]:
    return update_pm_continuity(source_record)
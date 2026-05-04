from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = PM_CORE_DIR / "state" / "current"

PM_STRATEGY_STATE_PATH = STATE_DIR / "pm_strategy_state.json"
PM_DECISION_LEDGER_PATH = STATE_DIR / "pm_decision_ledger.json"

PM_STRATEGY_VERSION = "northstar_pm_strategy_v1"
MUTATION_CLASS = "memory_persistence"
RECEIPT_MUTATION_CLASS = "receipt"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_route_directly": False,
    "can_activate_child_core": False,
    "can_mutate_workflow_state": False,
    "can_override_refinement_arbitrator": False,
    "can_override_research_truth": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_strategy_memory_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(
    payload: Dict[str, Any],
    *,
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
    advisory_only: bool = True,
) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_version", PM_STRATEGY_VERSION)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = mutation_class
    normalized["advisory_only"] = advisory_only
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["routing_execution_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
    return normalized


def _governed_write(
    path: Path,
    payload: Dict[str, Any],
    *,
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
    advisory_only: bool = True,
) -> str:
    normalized = _normalize_payload(
        payload,
        persistence_type=persistence_type,
        mutation_class=mutation_class,
        advisory_only=advisory_only,
    )

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": advisory_only,
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
            "artifact_type": "pm_strategy_state",
            "artifact_version": PM_STRATEGY_VERSION,
            "updated_at": _utc_now(),
            "total_decisions": 0,
            "decision_counts_by_action": {},
            "decision_counts_by_core": {},
            "recent_decision_packet_ids": [],
        },
        persistence_type="pm_strategy_state",
    )


def _default_ledger() -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_decision_ledger",
            "artifact_version": PM_STRATEGY_VERSION,
            "updated_at": _utc_now(),
            "entries": [],
        },
        persistence_type="pm_decision_ledger",
    )


def load_pm_strategy_state() -> Dict[str, Any]:
    return _normalize_payload(
        _read_json(PM_STRATEGY_STATE_PATH, _default_state()),
        persistence_type="pm_strategy_state",
    )


def load_pm_decision_ledger() -> Dict[str, Any]:
    return _normalize_payload(
        _read_json(PM_DECISION_LEDGER_PATH, _default_ledger()),
        persistence_type="pm_decision_ledger",
    )


def build_pm_decision_packet(
    *,
    pm_continuity_update: Dict[str, Any],
    target_child_core_id: Optional[str] = None,
    recommended_action: Optional[str] = None,
    rationale: str = "",
) -> Dict[str, Any]:
    continuity = pm_continuity_update if isinstance(pm_continuity_update, dict) else {}
    state = continuity.get("state") if isinstance(continuity.get("state"), dict) else {}

    child_counts = state.get("child_core_counts") if isinstance(state.get("child_core_counts"), dict) else {}
    action_counts = state.get("action_counts") if isinstance(state.get("action_counts"), dict) else {}

    resolved_child_core = target_child_core_id or max(child_counts, key=child_counts.get, default="unknown")
    resolved_action = recommended_action or max(action_counts, key=action_counts.get, default="hold")

    return _normalize_payload(
        {
            "artifact_type": "pm_decision_packet",
            "artifact_version": PM_STRATEGY_VERSION,
            "decision_packet_id": f"pm_decision_{_utc_now().replace(':', '-')}",
            "created_at": _utc_now(),
            "target_child_core_id": resolved_child_core,
            "recommended_action": resolved_action,
            "rationale": rationale or "PM strategy consolidated continuity signals into advisory decision packet.",
            "source_update_id": continuity.get("update_id"),
            "source_state_path": continuity.get("state_path"),
            "summary": {
                "child_core_counts": child_counts,
                "action_counts": action_counts,
            },
        },
        persistence_type="pm_decision_packet",
    )


def persist_pm_decision_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized_packet = _normalize_payload(
        packet,
        persistence_type="pm_decision_packet",
        mutation_class=MUTATION_CLASS,
        advisory_only=True,
    )

    state = load_pm_strategy_state()
    ledger = load_pm_decision_ledger()

    decision_id = str(normalized_packet.get("decision_packet_id", "pm_decision_unknown"))
    action = str(normalized_packet.get("recommended_action", "unknown"))
    core = str(normalized_packet.get("target_child_core_id", "unknown"))

    action_counts = state.get("decision_counts_by_action", {})
    if not isinstance(action_counts, dict):
        action_counts = {}
    action_counts[action] = int(action_counts.get(action, 0) or 0) + 1

    core_counts = state.get("decision_counts_by_core", {})
    if not isinstance(core_counts, dict):
        core_counts = {}
    core_counts[core] = int(core_counts.get(core, 0) or 0) + 1

    recent = state.get("recent_decision_packet_ids", [])
    if not isinstance(recent, list):
        recent = []
    recent.append(decision_id)

    state["updated_at"] = _utc_now()
    state["total_decisions"] = int(state.get("total_decisions", 0) or 0) + 1
    state["decision_counts_by_action"] = action_counts
    state["decision_counts_by_core"] = core_counts
    state["recent_decision_packet_ids"] = recent[-50:]

    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    entries.append(normalized_packet)

    ledger["entries"] = entries[-1000:]
    ledger["updated_at"] = _utc_now()

    state_path = _governed_write(PM_STRATEGY_STATE_PATH, state, persistence_type="pm_strategy_state")
    ledger_path = _governed_write(PM_DECISION_LEDGER_PATH, ledger, persistence_type="pm_decision_ledger")

    return {
        "status": "persisted",
        "decision_packet_id": decision_id,
        "state_path": state_path,
        "ledger_path": ledger_path,
        "packet": normalized_packet,
    }


def run_pm_strategy(
    *,
    pm_continuity_update: Dict[str, Any],
    target_child_core_id: Optional[str] = None,
    recommended_action: Optional[str] = None,
    rationale: str = "",
) -> Dict[str, Any]:
    packet = build_pm_decision_packet(
        pm_continuity_update=pm_continuity_update,
        target_child_core_id=target_child_core_id,
        recommended_action=recommended_action,
        rationale=rationale,
    )
    return persist_pm_decision_packet(packet)
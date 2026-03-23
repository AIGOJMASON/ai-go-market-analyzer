from __future__ import annotations

import json
import os
from typing import Dict, Any, Mapping
from datetime import datetime, timezone
from uuid import uuid4

from strategic_decision_state import StrategicDecisionState
from decision_packet_builder import build_decision_packet


REQUIRED_CONTINUITY_FIELDS = [
    "update_type",
    "source_pm_intake_id",
    "source_arbitration_id",
    "source_packet_id",
    "recommended_action",
    "target_child_core",
    "state_snapshot",
    "timestamp",
]


class PMStrategyError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_strategy_receipt_id() -> str:
    return f"PMS-{uuid4().hex[:12].upper()}"


def _repo_root() -> str:
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _state_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "PM_CORE", "state", "current"))


def _state_path(filename: str) -> str:
    return os.path.join(_state_dir(), filename)


def _read_json(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if not os.path.exists(path):
        return dict(default)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str, payload: Mapping[str, Any]) -> str:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return path


def validate_continuity_update(continuity_update: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_CONTINUITY_FIELDS if field not in continuity_update]
    if missing:
        raise PMStrategyError(f"Missing required continuity fields: {', '.join(missing)}")
    if continuity_update.get("update_type") != "pm_continuity_update":
        raise PMStrategyError("PM_STRATEGY accepts only pm_continuity_update artifacts.")


def update_strategy_state(state: StrategicDecisionState, decision_packet: Dict[str, Any]) -> StrategicDecisionState:
    state.total_decisions += 1
    state.last_decision_id = decision_packet["packet_id"]

    action = decision_packet.get("recommended_action", "")
    core = decision_packet.get("target_child_core", "none") or "none"

    state.decision_counts_by_action[action] = state.decision_counts_by_action.get(action, 0) + 1
    state.decision_counts_by_core[core] = state.decision_counts_by_core.get(core, 0) + 1

    state.recent_decision_ids.append(decision_packet["packet_id"])
    state.recent_decision_ids = state.recent_decision_ids[-10:]
    state.last_updated = utc_now()
    return state


def _default_state() -> Dict[str, Any]:
    return StrategicDecisionState().to_dict()


def _default_ledger() -> Dict[str, Any]:
    return {
        "ledger_id": "PM_DECISION_LEDGER",
        "status": "active",
        "entry_count": 0,
        "entries": [],
        "last_updated": "",
    }


def _build_decision_entry(decision_packet: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    return {
        "entry_id": f"PMDL-{uuid4().hex[:12].upper()}",
        "entry_type": "pm_strategic_decision",
        "packet_id": decision_packet["packet_id"],
        "source_pm_intake_id": decision_packet["source_pm_intake_id"],
        "source_arbitration_id": decision_packet["source_arbitration_id"],
        "source_packet_id": decision_packet["source_packet_id"],
        "recommended_action": decision_packet["recommended_action"],
        "target_child_core": decision_packet.get("target_child_core"),
        "summary": decision_packet["strategy_summary"],
        "timestamp": timestamp,
    }


def run_pm_strategy(continuity_update: Dict[str, Any], *, persist: bool = True) -> Dict[str, Any]:
    validate_continuity_update(continuity_update)
    timestamp = utc_now()

    decision_packet = build_decision_packet(continuity_update)

    state_path = _state_path("pm_strategy_state.json")
    ledger_path = _state_path("pm_decision_ledger.json")

    loaded_state = _read_json(state_path, _default_state())
    state = StrategicDecisionState(
        state_id=str(loaded_state.get("state_id", "PM_STRATEGY_STATE")),
        total_decisions=int(loaded_state.get("total_decisions", 0)),
        last_decision_id=str(loaded_state.get("last_decision_id", "")),
        decision_counts_by_action=dict(loaded_state.get("decision_counts_by_action", {})),
        decision_counts_by_core=dict(loaded_state.get("decision_counts_by_core", {})),
        recent_decision_ids=list(loaded_state.get("recent_decision_ids", [])),
        last_updated=str(loaded_state.get("last_updated", "")),
    )
    state = update_strategy_state(state, decision_packet)
    state_dict = state.to_dict()

    ledger = _read_json(ledger_path, _default_ledger())
    decision_entry = _build_decision_entry(decision_packet, timestamp)
    entries = list(ledger.get("entries", []))
    entries.append(decision_entry)
    ledger["entries"] = entries
    ledger["entry_count"] = len(entries)
    ledger["last_updated"] = timestamp

    receipt = {
        "receipt_type": "pm_strategy_receipt",
        "receipt_id": build_strategy_receipt_id(),
        "decision_id": decision_packet["packet_id"],
        "source_pm_intake_id": continuity_update["source_pm_intake_id"],
        "source_arbitration_id": continuity_update["source_arbitration_id"],
        "source_packet_id": continuity_update["source_packet_id"],
        "timestamp": timestamp,
    }

    paths: Dict[str, str] = {}
    if persist:
        paths["state_path"] = _write_json(state_path, state_dict)
        paths["ledger_path"] = _write_json(ledger_path, ledger)

    return {
        "decision_packet": decision_packet,
        "state": state_dict,
        "decision_entry": decision_entry,
        "receipt": receipt,
        "paths": paths,
    }
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Mapping
from uuid import uuid4

from pm_change_ledger import append_change_entry, build_change_entry, default_change_ledger
from pm_continuity_state import PMContinuityState, update_state_from_pm_intake
from pm_unresolved_queue import (
    append_unresolved_entry,
    build_unresolved_entry,
    default_unresolved_queue,
    should_queue_unresolved,
)


REQUIRED_PM_INTAKE_FIELDS = [
    "pm_intake_id",
    "source_arbitration_id",
    "source_packet_id",
    "status",
    "recommended_action",
    "target_child_core",
    "timestamp",
]


class PMContinuityError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_continuity_id() -> str:
    return f"PMC-{uuid4().hex[:12].upper()}"


def build_ledger_entry_id() -> str:
    return f"PMCL-{uuid4().hex[:12].upper()}"


def build_unresolved_id() -> str:
    return f"PMU-{uuid4().hex[:12].upper()}"


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


def validate_pm_intake_record(record: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_PM_INTAKE_FIELDS if field not in record]
    if missing:
        raise PMContinuityError(f"Missing required PM intake fields: {', '.join(missing)}")


def update_pm_continuity(pm_artifact: Mapping[str, Any], *, persist: bool = True) -> Dict[str, Any]:
    validate_pm_intake_record(pm_artifact)
    timestamp = utc_now()

    state_path = _state_path("pm_continuity_state.json")
    ledger_path = _state_path("pm_change_ledger.json")
    unresolved_path = _state_path("pm_unresolved_queue.json")

    loaded_state = _read_json(state_path, PMContinuityState().to_dict())
    state = PMContinuityState(
        state_id=str(loaded_state.get("state_id", "PM_CONTINUITY_STATE")),
        status=str(loaded_state.get("status", "active")),
        total_pm_intake_records=int(loaded_state.get("total_pm_intake_records", 0)),
        total_continuity_updates=int(loaded_state.get("total_continuity_updates", 0)),
        recommended_action_counts=dict(loaded_state.get("recommended_action_counts", {})),
        target_child_core_counts=dict(loaded_state.get("target_child_core_counts", {})),
        recent_pm_intake_ids=list(loaded_state.get("recent_pm_intake_ids", [])),
        recent_source_arbitration_ids=list(loaded_state.get("recent_source_arbitration_ids", [])),
        recent_source_packet_ids=list(loaded_state.get("recent_source_packet_ids", [])),
        unresolved_count=int(loaded_state.get("unresolved_count", 0)),
        last_updated=str(loaded_state.get("last_updated", "")),
    )
    state = update_state_from_pm_intake(state, dict(pm_artifact), timestamp=timestamp)

    ledger = _read_json(ledger_path, default_change_ledger())
    ledger_entry = build_change_entry(
        entry_id=build_ledger_entry_id(),
        source_pm_intake_id=str(pm_artifact["pm_intake_id"]),
        source_arbitration_id=str(pm_artifact["source_arbitration_id"]),
        source_packet_id=str(pm_artifact["source_packet_id"]),
        recommended_action=str(pm_artifact["recommended_action"]),
        target_child_core=pm_artifact.get("target_child_core"),
        summary=(
            f"PM continuity recorded intake {pm_artifact['pm_intake_id']} with "
            f"recommended_action={pm_artifact['recommended_action']} and "
            f"target_child_core={pm_artifact.get('target_child_core') or 'none'}."
        ),
        timestamp=timestamp,
    )
    ledger = append_change_entry(ledger, ledger_entry)

    unresolved_queue = _read_json(unresolved_path, default_unresolved_queue())
    unresolved_entry = None
    if should_queue_unresolved(dict(pm_artifact)):
        unresolved_entry = build_unresolved_entry(
            unresolved_id=build_unresolved_id(),
            source_pm_intake_id=str(pm_artifact["pm_intake_id"]),
            source_arbitration_id=str(pm_artifact["source_arbitration_id"]),
            source_packet_id=str(pm_artifact["source_packet_id"]),
            recommended_action=str(pm_artifact["recommended_action"]),
            target_child_core=pm_artifact.get("target_child_core"),
            reason=(
                f"PM continuity observed unresolved action {pm_artifact['recommended_action']} "
                f"for target_child_core={pm_artifact.get('target_child_core') or 'none'}."
            ),
            timestamp=timestamp,
        )
        unresolved_queue = append_unresolved_entry(unresolved_queue, unresolved_entry)
        state.unresolved_count = int(unresolved_queue.get("entry_count", 0))
    else:
        state.unresolved_count = int(unresolved_queue.get("entry_count", 0))

    state_dict = state.to_dict()

    receipt = {
        "receipt_type": "pm_continuity_receipt",
        "continuity_id": build_continuity_id(),
        "source_pm_intake_id": pm_artifact["pm_intake_id"],
        "source_arbitration_id": pm_artifact["source_arbitration_id"],
        "source_packet_id": pm_artifact["source_packet_id"],
        "recommended_action": pm_artifact["recommended_action"],
        "target_child_core": pm_artifact.get("target_child_core"),
        "timestamp": timestamp,
    }

    paths: Dict[str, str] = {}
    if persist:
        paths["state_path"] = _write_json(state_path, state_dict)
        paths["ledger_path"] = _write_json(ledger_path, ledger)
        paths["unresolved_path"] = _write_json(unresolved_path, unresolved_queue)

    return {
        "update": {
            "update_type": "pm_continuity_update",
            "source_pm_intake_id": pm_artifact["pm_intake_id"],
            "source_arbitration_id": pm_artifact["source_arbitration_id"],
            "source_packet_id": pm_artifact["source_packet_id"],
            "recommended_action": pm_artifact["recommended_action"],
            "target_child_core": pm_artifact.get("target_child_core"),
            "state_snapshot": state_dict,
            "ledger_entry": ledger_entry,
            "unresolved_entry": unresolved_entry,
            "timestamp": timestamp,
        },
        "receipt": receipt,
        "paths": paths,
    }
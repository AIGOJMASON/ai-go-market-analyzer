from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "contractor_proposals_core"
CORE_ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = CORE_ROOT / "state" / "current"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _smi_record_path(packet_id: str) -> Path:
    return STATE_DIR / f"{packet_id}__core_smi_record.json"


def _smi_state_path() -> Path:
    return STATE_DIR / "core_smi_state.json"


def record_child_core_continuity(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy surface retired for Stage 23 compliance.

    Continuity mutation may not be invoked from legacy child-core execution
    flow. Continuity must be introduced only by a later governed stage.
    """
    packet_id = event.get("packet_id", "unknown_packet")
    record = {
        "core_id": CORE_ID,
        "packet_id": packet_id,
        "recorded_at": _utc_now(),
        "status": "blocked",
        "reason": "continuity_invocation_not_lawful_before_governed_continuity_stage",
        "allowed_future_boundary": "stage25_continuity",
        "received_event": event,
    }
    record_path = _smi_record_path(packet_id)
    _write_json(record_path, record)

    state = {
        "core_id": CORE_ID,
        "last_packet_id": packet_id,
        "last_record_path": record_path.as_posix(),
        "updated_at": _utc_now(),
        "status": "blocked_pending_governed_continuity_stage",
    }
    _write_json(_smi_state_path(), state)

    return {
        "status": "blocked",
        "smi_record_path": record_path.as_posix(),
        "reason": record["reason"],
    }
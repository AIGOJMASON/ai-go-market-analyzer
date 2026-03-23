from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "contractor_proposals_core"
DOMAIN_FOCUS = "contractor_proposals"
CORE_ROOT = Path(__file__).resolve().parents[1]
INHERITANCE_STATE_DIR = CORE_ROOT / "inheritance_state"
EXECUTION_DIR = CORE_ROOT / "execution"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Expected top-level dict JSON artifact")

    return payload


def _inheritance_state_path(packet_id: str) -> Path:
    return INHERITANCE_STATE_DIR / f"{packet_id}__inheritance_state.json"


def _execution_record_path(packet_id: str) -> Path:
    return EXECUTION_DIR / f"{packet_id}__execution_record.json"


def process_ingress(ingress_receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy compatibility adapter.

    This surface no longer constructs outputs, calls watcher verification,
    or mutates child-core continuity. It records bounded state and prepares
    the runtime handoff only.
    """
    if ingress_receipt.get("status") != "delivered":
        raise ValueError("Ingress receipt is not in delivered state.")
    if ingress_receipt.get("target_core_id") != CORE_ID:
        raise ValueError("Ingress receipt target_core_id does not match contractor_proposals_core.")
    if ingress_receipt.get("domain_focus") != DOMAIN_FOCUS:
        raise ValueError("Ingress receipt domain_focus does not match contractor_proposals.")

    packet_id = ingress_receipt["packet_id"]
    inheritance_packet = _read_json(ingress_receipt["inheritance_packet_path"])

    inheritance_state = {
        "status": "inheritance_state_recorded",
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "packet_id": packet_id,
        "inheritance_packet_path": ingress_receipt["inheritance_packet_path"],
        "recorded_at": _utc_now(),
        "boundary_note": "Recorded by legacy ingress adapter. No execution, output, watcher, or continuity side effects are permitted here.",
    }
    inheritance_state_path = _inheritance_state_path(packet_id)
    _write_json(inheritance_state_path, inheritance_state)

    research_packet = inheritance_packet.get("research_packet", {})
    execution_record = {
        "status": "prepared_for_runtime",
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "packet_id": packet_id,
        "proposal_type": "contractor_estimate_packet",
        "client_request_summary": research_packet.get("summary", ""),
        "recommended_sections": [
            "project_overview",
            "scope_of_work",
            "pricing_assumptions",
            "schedule",
            "terms_and_acceptance",
        ],
        "next_action": "prepare bounded proposal draft from PM inheritance",
        "inheritance_state_path": inheritance_state_path.as_posix(),
        "ingress_receipt_path": ingress_receipt.get("child_core_ingress_receipt_path"),
        "executed_at": _utc_now(),
        "execution_mode": "bounded_runtime_handoff",
        "next_surface": "child_cores.runtime.child_core_runtime",
        "allowed_side_effects": [],
        "forbidden_side_effects": [
            "output_construction",
            "watcher_trigger",
            "continuity_update",
            "publication",
        ],
    }
    execution_record_path = _execution_record_path(packet_id)
    _write_json(execution_record_path, execution_record)

    return {
        "status": "prepared_for_runtime",
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "execution_record_path": execution_record_path.as_posix(),
        "inheritance_state_path": inheritance_state_path.as_posix(),
        "next_surface": "child_cores.runtime.child_core_runtime",
        "next_boundary": "stage22_runtime",
        "output_allowed": False,
        "watcher_allowed": False,
        "continuity_allowed": False,
    }
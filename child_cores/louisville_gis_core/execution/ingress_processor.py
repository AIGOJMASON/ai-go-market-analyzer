from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "louisville_gis_core"
DOMAIN_FOCUS = "louisville_gis"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_core_root() -> Path:
    return get_project_root() / "child_cores" / CORE_ID


def get_inheritance_state_dir() -> Path:
    return get_core_root() / "inheritance_state"


def get_execution_dir() -> Path:
    return get_core_root() / "execution"


def _load_json(path: str | Path) -> Dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Expected top-level dict JSON artifact")

    return payload


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return str(path)


def process_louisville_gis_ingress(
    *,
    receipt_path: str,
) -> Dict[str, Any]:
    """
    Legacy compatibility adapter.

    This surface no longer performs output construction, watcher verification,
    or continuity mutation. It only validates the ingress artifact, records
    bounded child-core state, and prepares a runtime handoff record.
    """
    receipt = _load_json(receipt_path)

    if receipt.get("receiving_authority") != CORE_ID:
        return {
            "status": "failed",
            "reason": "wrong_receiving_authority",
            "receipt_path": receipt_path,
            "expected_receiving_authority": CORE_ID,
        }

    inheritance_packet_path = receipt.get("inheritance_packet_path")
    if not isinstance(inheritance_packet_path, str) or not inheritance_packet_path.strip():
        return {
            "status": "failed",
            "reason": "missing_inheritance_packet_path",
            "receipt_path": receipt_path,
        }

    inheritance_packet = _load_json(inheritance_packet_path)

    if inheritance_packet.get("packet_type") != "pm_inheritance_packet":
        return {
            "status": "failed",
            "reason": "wrong_inheritance_packet_type",
            "receipt_path": receipt_path,
            "inheritance_packet_path": inheritance_packet_path,
            "expected_packet_type": "pm_inheritance_packet",
        }

    if inheritance_packet.get("inheritance_target") != "child_core_candidate":
        return {
            "status": "failed",
            "reason": "inheritance_target_not_child_core_candidate",
            "receipt_path": receipt_path,
            "inheritance_packet_path": inheritance_packet_path,
        }

    inheritance_state_result = _persist_inheritance_state(
        receipt=receipt,
        inheritance_packet=inheritance_packet,
    )

    execution_record = _build_execution_record(
        receipt=receipt,
        inheritance_packet=inheritance_packet,
        inheritance_state_path=inheritance_state_result["inheritance_state_path"],
    )
    execution_result = _persist_execution_record(execution_record)

    return {
        "status": "prepared_for_runtime",
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "receipt_path": receipt_path,
        "inheritance_packet_path": inheritance_packet_path,
        "inheritance_state_result": inheritance_state_result,
        "execution_result": execution_result,
        "next_surface": "child_cores.runtime.child_core_runtime",
        "next_boundary": "stage22_runtime",
        "output_allowed": False,
        "watcher_allowed": False,
        "continuity_allowed": False,
    }


def _persist_inheritance_state(
    *,
    receipt: Dict[str, Any],
    inheritance_packet: Dict[str, Any],
) -> Dict[str, Any]:
    inheritance_packet_id = inheritance_packet.get("inheritance_packet_id") or "unknown_inheritance_packet"
    path = get_inheritance_state_dir() / f"{inheritance_packet_id}__inheritance_state.json"

    state_payload = {
        "state_type": "child_core_inheritance_state",
        "recorded_at": _utc_now_iso(),
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "status": "recorded",
        "ingress_receipt": receipt,
        "inheritance_packet": inheritance_packet,
        "boundary_note": "Recorded by legacy ingress adapter. No execution, output, watcher, or continuity side effects are permitted here.",
    }

    written_path = _write_json(path, state_payload)

    return {
        "status": "recorded",
        "inheritance_state_path": written_path,
        "inheritance_state": state_payload,
    }


def _build_execution_record(
    *,
    receipt: Dict[str, Any],
    inheritance_packet: Dict[str, Any],
    inheritance_state_path: str,
) -> Dict[str, Any]:
    source_packet_id = inheritance_packet.get("source_packet_id") or "unknown_source_packet"

    return {
        "execution_type": "child_core_execution_record",
        "execution_id": f"WR-EXEC-LOUISVILLE-GIS-{source_packet_id}",
        "recorded_at": _utc_now_iso(),
        "core_id": CORE_ID,
        "domain_focus": DOMAIN_FOCUS,
        "status": "prepared_for_runtime",
        "execution_mode": "bounded_runtime_handoff",
        "source_packet_id": source_packet_id,
        "inheritance_packet_id": inheritance_packet.get("inheritance_packet_id"),
        "ingress_receipt_path": receipt.get("receipt_path", receipt.get("child_core_ingress_receipt_path")),
        "inheritance_state_path": inheritance_state_path,
        "domain_action": "prepare_louisville_gis_review",
        "constraints": inheritance_packet.get("constraints", []),
        "next_surface": "child_cores.runtime.child_core_runtime",
        "allowed_side_effects": [],
        "forbidden_side_effects": [
            "output_construction",
            "watcher_trigger",
            "continuity_update",
            "publication",
        ],
    }


def _persist_execution_record(
    execution_record: Dict[str, Any],
) -> Dict[str, Any]:
    execution_id = execution_record.get("execution_id") or "unknown_execution"
    path = get_execution_dir() / f"{execution_id}.json"
    written_path = _write_json(path, execution_record)

    return {
        "status": "recorded",
        "execution_record_path": written_path,
        "execution_record": execution_record,
    }
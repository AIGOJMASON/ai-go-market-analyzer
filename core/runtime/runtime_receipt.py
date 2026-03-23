from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_RECEIPTS_DIR = ROOT / "state" / "monitoring" / "current"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_runtime_receipt(runtime_result: Dict[str, Any]) -> str:
    packet_id = runtime_result.get("packet_id", f"runtime_{_utc_now()}")
    receipt_path = RUNTIME_RECEIPTS_DIR / f"{packet_id}__runtime_receipt.json"

    receipt = {
        "status": runtime_result.get("status", "runtime_complete"),
        "generated_at": _utc_now(),
        "packet_id": packet_id,
        "research_packet_path": runtime_result.get("research_packet_path"),
        "watcher_status": runtime_result.get("watcher_status"),
        "smi_status": runtime_result.get("smi_status"),
        "pm_status": runtime_result.get("pm_status"),
        "pm_receipt_path": runtime_result.get("pm_receipt_path"),
        "inheritance_packet_path": runtime_result.get("inheritance_packet_path"),
        "refinement_status": runtime_result.get("refinement_status"),
        "selected_engines": runtime_result.get("selected_engines"),
        "refinement_receipt_paths": runtime_result.get("refinement_receipt_paths"),
        "refinement_artifact_paths": runtime_result.get("refinement_artifact_paths"),
        "routing_decision_path": runtime_result.get("routing_decision_path"),
        "routing_status": runtime_result.get("routing_status"),
        "routing_reason": runtime_result.get("routing_reason"),
        "routing_confidence": runtime_result.get("routing_confidence"),
        "child_core_handoff_status": runtime_result.get("child_core_handoff_status"),
        "target_core_id": runtime_result.get("target_core_id"),
        "child_core_ingress_receipt_path": runtime_result.get("child_core_ingress_receipt_path"),
        "child_core_execution_status": runtime_result.get("child_core_execution_status"),
        "child_core_execution_record_path": runtime_result.get("child_core_execution_record_path"),
        "child_core_output_path": runtime_result.get("child_core_output_path"),
        "child_core_watcher_status": runtime_result.get("child_core_watcher_status"),
        "child_core_watcher_receipt_path": runtime_result.get("child_core_watcher_receipt_path"),
        "child_core_smi_status": runtime_result.get("child_core_smi_status"),
        "child_core_smi_record_path": runtime_result.get("child_core_smi_record_path"),
        "transitions_path": runtime_result.get("transitions_path"),
        "sentinel_status": runtime_result.get("sentinel_status"),
        "sentinel_status_path": runtime_result.get("sentinel_status_path"),
        "unresolved_queue_path": runtime_result.get("unresolved_queue_path"),
    }
    _write_json(receipt_path, receipt)
    return receipt_path.as_posix()
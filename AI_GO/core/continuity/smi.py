from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from core.continuity.change_ledger import record_change
from core.continuity.continuity_state import append_smi_event


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_research_packet_event(
    *,
    packet_id: str,
    packet_path: str,
    watcher_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Record continuity only after watcher verification succeeds.

    This is the lawful SMI orchestration surface for Stage Three.
    """
    if watcher_result.get("status") != "verified":
        return {
            "status": "skipped",
            "reason": "watcher_not_verified",
            "packet_id": packet_id,
            "packet_path": packet_path,
            "watcher_result": watcher_result,
        }

    recorded_at = utc_now_iso()

    event = {
        "event_type": "research_packet_verified",
        "packet_id": packet_id,
        "packet_path": packet_path,
        "watcher_status": watcher_result.get("status"),
        "recorded_at": recorded_at,
        "notes": "Verified research packet recorded into continuity state.",
    }

    change = {
        "change_type": "accepted_continuity_change",
        "source_surface": "core.continuity.smi",
        "reason": "Verified research packet generation completed successfully.",
        "packet_id": packet_id,
        "packet_path": packet_path,
        "recorded_at": recorded_at,
    }

    continuity_result = None
    ledger_result = None

    try:
        continuity_result = append_smi_event(event)
        ledger_result = record_change(change)
    except Exception as exc:
        return {
            "status": "failed",
            "packet_id": packet_id,
            "packet_path": packet_path,
            "watcher_result": watcher_result,
            "continuity_result": continuity_result,
            "ledger_result": ledger_result,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        }

    return {
        "status": "recorded",
        "packet_id": packet_id,
        "packet_path": packet_path,
        "continuity_result": continuity_result,
        "ledger_result": ledger_result,
    }
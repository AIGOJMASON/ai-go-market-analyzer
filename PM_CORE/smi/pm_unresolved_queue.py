from __future__ import annotations

from typing import Any, Dict, List


UNRESOLVED_ACTIONS = {
    "hold",
    "discard",
}


def should_queue_unresolved(pm_intake_record: Dict[str, Any]) -> bool:
    action = str(pm_intake_record.get("recommended_action", ""))
    return action in UNRESOLVED_ACTIONS


def build_unresolved_entry(
    *,
    unresolved_id: str,
    source_pm_intake_id: str,
    source_arbitration_id: str,
    source_packet_id: str,
    recommended_action: str,
    target_child_core: str | None,
    reason: str,
    timestamp: str,
) -> Dict[str, Any]:
    return {
        "unresolved_id": unresolved_id,
        "status": "open",
        "source_pm_intake_id": source_pm_intake_id,
        "source_arbitration_id": source_arbitration_id,
        "source_packet_id": source_packet_id,
        "recommended_action": recommended_action,
        "target_child_core": target_child_core,
        "reason": reason,
        "timestamp": timestamp,
    }


def append_unresolved_entry(queue: Dict[str, Any], entry: Dict[str, Any]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = list(queue.get("entries", []))
    entries.append(entry)
    queue["entries"] = entries
    queue["entry_count"] = len(entries)
    queue["last_updated"] = entry["timestamp"]
    return queue


def default_unresolved_queue() -> Dict[str, Any]:
    return {
        "queue_id": "PM_UNRESOLVED_QUEUE",
        "status": "active",
        "entry_count": 0,
        "entries": [],
        "last_updated": "",
    }
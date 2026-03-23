from __future__ import annotations

from typing import Any, Dict, List


def build_change_entry(
    *,
    entry_id: str,
    source_pm_intake_id: str,
    source_arbitration_id: str,
    source_packet_id: str,
    recommended_action: str,
    target_child_core: str | None,
    summary: str,
    timestamp: str,
) -> Dict[str, Any]:
    return {
        "entry_id": entry_id,
        "entry_type": "pm_continuity_change",
        "source_pm_intake_id": source_pm_intake_id,
        "source_arbitration_id": source_arbitration_id,
        "source_packet_id": source_packet_id,
        "recommended_action": recommended_action,
        "target_child_core": target_child_core,
        "summary": summary,
        "timestamp": timestamp,
    }


def append_change_entry(ledger: Dict[str, Any], entry: Dict[str, Any]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = list(ledger.get("entries", []))
    entries.append(entry)
    ledger["entries"] = entries
    ledger["entry_count"] = len(entries)
    ledger["last_updated"] = entry["timestamp"]
    return ledger


def default_change_ledger() -> Dict[str, Any]:
    return {
        "ledger_id": "PM_CHANGE_LEDGER",
        "status": "active",
        "entry_count": 0,
        "entries": [],
        "last_updated": "",
    }
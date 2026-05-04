from __future__ import annotations

from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_decision_packet(continuity_update: Dict[str, Any]) -> Dict[str, Any]:
    state_snapshot = continuity_update.get("state_snapshot", {})
    ledger_entry = continuity_update.get("ledger_entry", {})
    target_child_core = continuity_update.get("target_child_core")
    recommended_action = continuity_update.get("recommended_action", "")

    return {
        "packet_id": f"PM-DEC-{uuid4().hex[:10].upper()}",
        "packet_type": "pm_decision_packet",
        "issuing_layer": "PM_STRATEGY",
        "source_pm_intake_id": continuity_update["source_pm_intake_id"],
        "source_arbitration_id": continuity_update["source_arbitration_id"],
        "source_packet_id": continuity_update["source_packet_id"],
        "recommended_action": recommended_action,
        "target_child_core": target_child_core,
        "continuity_reference": {
            "state_id": state_snapshot.get("state_id"),
            "total_pm_intake_records": state_snapshot.get("total_pm_intake_records"),
            "recommended_action_counts": state_snapshot.get("recommended_action_counts", {}),
            "target_child_core_counts": state_snapshot.get("target_child_core_counts", {}),
        },
        "strategy_summary": (
            f"PM strategy consolidated continuity from {continuity_update['source_pm_intake_id']} "
            f"with recommended_action={recommended_action} and "
            f"target_child_core={target_child_core or 'none'}."
        ),
        "continuity_ledger_reference": ledger_entry.get("entry_id"),
        "timestamp": utc_now(),
    }
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PMContinuityState:
    state_id: str = "PM_CONTINUITY_STATE"
    status: str = "active"
    total_pm_intake_records: int = 0
    total_continuity_updates: int = 0
    recommended_action_counts: Dict[str, int] = field(default_factory=dict)
    target_child_core_counts: Dict[str, int] = field(default_factory=dict)
    recent_pm_intake_ids: List[str] = field(default_factory=list)
    recent_source_arbitration_ids: List[str] = field(default_factory=list)
    recent_source_packet_ids: List[str] = field(default_factory=list)
    unresolved_count: int = 0
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "status": self.status,
            "total_pm_intake_records": self.total_pm_intake_records,
            "total_continuity_updates": self.total_continuity_updates,
            "recommended_action_counts": dict(self.recommended_action_counts),
            "target_child_core_counts": dict(self.target_child_core_counts),
            "recent_pm_intake_ids": list(self.recent_pm_intake_ids),
            "recent_source_arbitration_ids": list(self.recent_source_arbitration_ids),
            "recent_source_packet_ids": list(self.recent_source_packet_ids),
            "unresolved_count": self.unresolved_count,
            "last_updated": self.last_updated,
        }


def append_recent(items: List[str], value: str, limit: int = 10) -> List[str]:
    if value:
        items.append(value)
    return items[-limit:]


def increment_count(counter: Dict[str, int], key: str) -> Dict[str, int]:
    if not key:
        return counter
    counter[key] = int(counter.get(key, 0)) + 1
    return counter


def update_state_from_pm_intake(
    state: PMContinuityState,
    pm_intake_record: Dict[str, Any],
    *,
    timestamp: str,
) -> PMContinuityState:
    state.total_pm_intake_records += 1
    state.total_continuity_updates += 1
    increment_count(state.recommended_action_counts, str(pm_intake_record.get("recommended_action", "")))
    increment_count(state.target_child_core_counts, str(pm_intake_record.get("target_child_core") or "none"))
    state.recent_pm_intake_ids = append_recent(state.recent_pm_intake_ids, str(pm_intake_record.get("pm_intake_id", "")))
    state.recent_source_arbitration_ids = append_recent(
        state.recent_source_arbitration_ids,
        str(pm_intake_record.get("source_arbitration_id", "")),
    )
    state.recent_source_packet_ids = append_recent(
        state.recent_source_packet_ids,
        str(pm_intake_record.get("source_packet_id", "")),
    )
    state.last_updated = timestamp
    return state
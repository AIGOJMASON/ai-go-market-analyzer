from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class StrategicDecisionState:
    state_id: str = "PM_STRATEGY_STATE"
    total_decisions: int = 0
    last_decision_id: str = ""
    decision_counts_by_action: Dict[str, int] = field(default_factory=dict)
    decision_counts_by_core: Dict[str, int] = field(default_factory=dict)
    recent_decision_ids: List[str] = field(default_factory=list)
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "total_decisions": self.total_decisions,
            "last_decision_id": self.last_decision_id,
            "decision_counts_by_action": self.decision_counts_by_action,
            "decision_counts_by_core": self.decision_counts_by_core,
            "recent_decision_ids": self.recent_decision_ids,
            "last_updated": self.last_updated,
        }
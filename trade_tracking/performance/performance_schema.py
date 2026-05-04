from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict


@dataclass
class TradePerformanceSummary:
    artifact_type: str
    generated_at: str
    system_id: str
    trade_count: int
    opened_trade_count: int
    closed_trade_count: int
    win_count: int
    loss_count: int
    flat_count: int
    win_rate: float
    average_realized_pnl_usd: float
    total_realized_pnl_usd: float
    by_symbol: Dict[str, Any] = field(default_factory=dict)
    by_event_theme: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
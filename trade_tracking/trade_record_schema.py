from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BaseTradeEvent:
    event_id: str
    event_type: str
    timestamp: str
    system_id: str
    strategy_id: str
    trade_id: str
    symbol: str
    event_theme: str
    action_class: str
    source_request_id: Optional[str] = None
    source_closeout_id: Optional[str] = None
    approval_required: Optional[bool] = None
    execution_allowed: Optional[bool] = None
    notes: Optional[str] = None
    artifact_type: str = "trade_tracking_event"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TradeOpenedEvent(BaseTradeEvent):
    entry_price: float = 0.0
    size_usd: float = 0.0
    quantity: float = 0.0


@dataclass
class TradeClosedEvent(BaseTradeEvent):
    exit_price: float = 0.0
    realized_pnl_usd: float = 0.0
    hold_duration_seconds: int = 0
    close_reason: str = "unspecified"
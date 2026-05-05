from __future__ import annotations

from typing import Dict, List, Set

ALLOWED_EVENT_TYPES: List[str] = [
    "trade_opened",
    "trade_closed",
]

ALLOWED_ACTION_CLASSES: List[str] = [
    "long",
    "short",
]

ALLOWED_SYSTEM_IDS: List[str] = [
    "system_a",
    "system_b",
]

REQUIRED_FIELDS_BY_EVENT_TYPE: Dict[str, Set[str]] = {
    "trade_opened": {
        "event_id",
        "event_type",
        "timestamp",
        "system_id",
        "strategy_id",
        "trade_id",
        "symbol",
        "event_theme",
        "action_class",
        "entry_price",
        "size_usd",
        "quantity",
    },
    "trade_closed": {
        "event_id",
        "event_type",
        "timestamp",
        "system_id",
        "strategy_id",
        "trade_id",
        "symbol",
        "event_theme",
        "action_class",
        "exit_price",
        "realized_pnl_usd",
        "hold_duration_seconds",
        "close_reason",
    },
}

INDEX_FILE_NAMES: Dict[str, str] = {
    "by_trade_id": "trade_index_by_trade_id.json",
    "by_symbol": "trade_index_by_symbol.json",
    "by_system_id": "trade_index_by_system_id.json",
    "latest_events": "latest_trade_events.json",
}

TRADE_TRACKING_ARTIFACT_TYPE = "trade_tracking_event"
TRADE_TRACKING_RECEIPT_TYPE = "trade_tracking_receipt"
TRADE_PERFORMANCE_SUMMARY_TYPE = "trade_performance_summary"
TRADE_PERFORMANCE_RECEIPT_TYPE = "trade_performance_receipt"
from __future__ import annotations

from typing import Any, Dict

from AI_GO.trade_tracking.id_builder import build_performance_receipt_id, build_trade_receipt_id
from AI_GO.trade_tracking.trade_tracking_registry import (
    TRADE_PERFORMANCE_RECEIPT_TYPE,
    TRADE_TRACKING_RECEIPT_TYPE,
)


def build_trade_write_receipt(
    *,
    event_record: Dict[str, Any],
    path: str,
) -> Dict[str, Any]:
    timestamp = event_record["timestamp"]
    event_id = event_record["event_id"]

    return {
        "artifact_type": TRADE_TRACKING_RECEIPT_TYPE,
        "receipt_id": build_trade_receipt_id(event_id=event_id, timestamp=timestamp),
        "timestamp": timestamp,
        "status": "written",
        "event_id": event_id,
        "trade_id": event_record["trade_id"],
        "event_type": event_record["event_type"],
        "system_id": event_record["system_id"],
        "symbol": event_record["symbol"],
        "path": path,
    }


def build_performance_receipt(
    *,
    system_id: str,
    generated_at: str,
    path: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": TRADE_PERFORMANCE_RECEIPT_TYPE,
        "receipt_id": build_performance_receipt_id(system_id=system_id, timestamp=generated_at),
        "generated_at": generated_at,
        "status": "written",
        "system_id": system_id,
        "path": path,
    }
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from AI_GO.trade_tracking.id_builder import (
    build_trade_event_id,
    build_trade_id,
    build_trade_receipt_id,
)
from AI_GO.trade_tracking.storage.event_store import write_event, list_events
from AI_GO.trade_tracking.storage.index_store import rebuild_indexes
from AI_GO.trade_tracking.trade_record_schema import TradeClosedEvent, TradeOpenedEvent
from AI_GO.trade_tracking.trade_tracking_registry import (
    ALLOWED_ACTION_CLASSES,
    ALLOWED_EVENT_TYPES,
    ALLOWED_SYSTEM_IDS,
    REQUIRED_FIELDS_BY_EVENT_TYPE,
)


MUTATION_CLASS = "trade_tracking_persistence"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_event(event: Dict[str, Any]) -> None:
    event_type = str(event.get("event_type", "")).strip()
    system_id = str(event.get("system_id", "")).strip()
    action_class = str(event.get("action_class", "")).strip()

    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported trade event_type: {event_type}")

    if system_id not in ALLOWED_SYSTEM_IDS:
        raise ValueError(f"Unsupported system_id: {system_id}")

    if action_class not in ALLOWED_ACTION_CLASSES:
        raise ValueError(f"Unsupported action_class: {action_class}")

    required = REQUIRED_FIELDS_BY_EVENT_TYPE.get(event_type, set())
    missing = sorted(field for field in required if event.get(field) in {None, ""})
    if missing:
        raise ValueError(f"Missing required trade fields: {missing}")


def _receipt_for_event(event: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    return {
        "artifact_type": "trade_tracking_receipt",
        "receipt_id": build_trade_receipt_id(
            event_id=str(event["event_id"]),
            timestamp=timestamp,
        ),
        "event_id": event["event_id"],
        "trade_id": event["trade_id"],
        "event_type": event["event_type"],
        "timestamp": timestamp,
        "status": "recorded",
        "persistence_type": "trade_tracking_receipt",
        "mutation_class": "receipt",
        "advisory_only": False,
        "execution_allowed": False,
    }


def _persist_event_and_indexes(event: Dict[str, Any]) -> Dict[str, Any]:
    _validate_event(event)

    event_write = write_event(event)
    index_write = rebuild_indexes(list_events())
    receipt = _receipt_for_event(event)

    return {
        "status": "persisted",
        "event_record": event_write["event_record"],
        "event_path": event_write["event_path"],
        "index_result": index_write,
        "receipt": receipt,
        "mutation_class": MUTATION_CLASS,
        "persistence_type": "trade_tracking_event_write",
        "advisory_only": False,
        "execution_allowed": False,
    }


def write_trade_opened(
    *,
    system_id: str,
    strategy_id: str,
    symbol: str,
    event_theme: str,
    action_class: str,
    entry_price: float,
    size_usd: float,
    quantity: float,
    source_request_id: Optional[str] = None,
    source_closeout_id: Optional[str] = None,
    approval_required: Optional[bool] = True,
    execution_allowed: Optional[bool] = False,
    notes: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    trade_id = build_trade_id(
        system_id=system_id,
        strategy_id=strategy_id,
        symbol=symbol,
        source_request_id=source_request_id,
        timestamp=timestamp,
    )

    event_id = build_trade_event_id(
        event_type="trade_opened",
        trade_id=trade_id,
        timestamp=timestamp,
    )

    event = TradeOpenedEvent(
        event_id=event_id,
        event_type="trade_opened",
        timestamp=timestamp,
        system_id=system_id,
        strategy_id=strategy_id,
        trade_id=trade_id,
        symbol=symbol,
        event_theme=event_theme,
        action_class=action_class,
        source_request_id=source_request_id,
        source_closeout_id=source_closeout_id,
        approval_required=approval_required,
        execution_allowed=execution_allowed,
        notes=notes,
        metadata=metadata or {},
        entry_price=float(entry_price),
        size_usd=float(size_usd),
        quantity=float(quantity),
    ).to_dict()

    event["persistence_type"] = "trade_tracking_event"
    event["mutation_class"] = MUTATION_CLASS
    event["advisory_only"] = False

    return _persist_event_and_indexes(event)


def write_trade_closed(
    *,
    system_id: str,
    strategy_id: str,
    trade_id: str,
    symbol: str,
    event_theme: str,
    action_class: str,
    exit_price: float,
    realized_pnl_usd: float,
    hold_duration_seconds: int,
    close_reason: str,
    source_request_id: Optional[str] = None,
    source_closeout_id: Optional[str] = None,
    approval_required: Optional[bool] = True,
    execution_allowed: Optional[bool] = False,
    notes: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    event_id = build_trade_event_id(
        event_type="trade_closed",
        trade_id=trade_id,
        timestamp=timestamp,
    )

    event = TradeClosedEvent(
        event_id=event_id,
        event_type="trade_closed",
        timestamp=timestamp,
        system_id=system_id,
        strategy_id=strategy_id,
        trade_id=trade_id,
        symbol=symbol,
        event_theme=event_theme,
        action_class=action_class,
        source_request_id=source_request_id,
        source_closeout_id=source_closeout_id,
        approval_required=approval_required,
        execution_allowed=execution_allowed,
        notes=notes,
        metadata=metadata or {},
        exit_price=float(exit_price),
        realized_pnl_usd=float(realized_pnl_usd),
        hold_duration_seconds=int(hold_duration_seconds),
        close_reason=close_reason,
    ).to_dict()

    event["persistence_type"] = "trade_tracking_event"
    event["mutation_class"] = MUTATION_CLASS
    event["advisory_only"] = False

    return _persist_event_and_indexes(event)
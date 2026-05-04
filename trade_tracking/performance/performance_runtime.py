from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.trade_tracking.performance.performance_state_writer import write_performance_state
from AI_GO.trade_tracking.storage.event_store import list_events


MUTATION_CLASS = "trade_tracking_persistence"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def build_performance_summary(system_id: str = "system_a") -> Dict[str, Any]:
    events = [
        event
        for event in list_events()
        if str(event.get("system_id", "")).strip() == system_id
    ]

    opened = [event for event in events if event.get("event_type") == "trade_opened"]
    closed = [event for event in events if event.get("event_type") == "trade_closed"]

    realized_pnl = sum(_safe_float(event.get("realized_pnl_usd")) for event in closed)

    by_symbol: Dict[str, Dict[str, Any]] = {}
    for event in events:
        symbol = str(event.get("symbol", "UNKNOWN")).strip() or "UNKNOWN"
        bucket = by_symbol.setdefault(
            symbol,
            {
                "symbol": symbol,
                "opened_count": 0,
                "closed_count": 0,
                "realized_pnl_usd": 0.0,
            },
        )

        if event.get("event_type") == "trade_opened":
            bucket["opened_count"] += 1
        if event.get("event_type") == "trade_closed":
            bucket["closed_count"] += 1
            bucket["realized_pnl_usd"] += _safe_float(event.get("realized_pnl_usd"))

    return {
        "artifact_type": "trade_performance_summary",
        "artifact_version": "northstar_trade_tracking_v1",
        "system_id": system_id,
        "generated_at": _utc_now(),
        "opened_count": len(opened),
        "closed_count": len(closed),
        "event_count": len(events),
        "realized_pnl_usd": realized_pnl,
        "by_symbol": by_symbol,
        "persistence_type": "trade_performance_summary",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": False,
        "execution_allowed": False,
        "derived_from_events": True,
    }


def persist_performance_summary(system_id: str = "system_a") -> Dict[str, Any]:
    summary = build_performance_summary(system_id=system_id)
    return write_performance_state(system_id, summary)


def run_performance_update(system_id: str = "system_a") -> Dict[str, Any]:
    return persist_performance_summary(system_id=system_id)
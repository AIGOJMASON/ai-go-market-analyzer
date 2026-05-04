from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from AI_GO.trade_tracking.trade_writer import write_trade_opened
except ImportError:
    from trade_tracking.trade_writer import write_trade_opened


def _safe_get(d: Dict[str, Any], *keys: str, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except:
        return None


def open_paper_trade_from_closeout(
    *,
    closeout_artifact: Dict[str, Any],
    size_usd: float = 10.0,
) -> Dict[str, Any]:

    symbol = (
        closeout_artifact.get("symbol")
        or _safe_get(closeout_artifact, "operator_packet", "current_case", "symbol")
    )

    entry_price = (
        _safe_float(closeout_artifact.get("reference_price"))
        or _safe_float(_safe_get(closeout_artifact, "operator_packet", "current_case", "reference_price"))
        or _safe_float(_safe_get(closeout_artifact, "market_panel", "reference_price"))
    )

    if not symbol or entry_price is None:
        raise ValueError("invalid trade input")

    quantity = round(size_usd / entry_price, 6)

    return write_trade_opened(
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        symbol=symbol,
        event_theme=_safe_get(closeout_artifact, "runtime_panel", "event_theme") or "unknown",
        action_class="long",
        entry_price=entry_price,
        size_usd=size_usd,
        quantity=quantity,
        metadata={"source": "system_a"},
    )
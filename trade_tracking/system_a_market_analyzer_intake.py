from __future__ import annotations

from typing import Any, Dict, Optional

from AI_GO.trade_tracking.trade_writer import write_trade_opened


MUTATION_CLASS = "trade_tracking_persistence"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_text(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def open_system_a_trade_from_market_analyzer(
    *,
    closeout_artifact: Dict[str, Any],
    size_usd: float = 10.0,
    action_class: str = "long",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    artifact = closeout_artifact if isinstance(closeout_artifact, dict) else {}

    symbol = _safe_text(artifact.get("symbol"), "UNKNOWN")
    event_theme = _safe_text(artifact.get("event_theme"), "market_analyzer_signal")
    source_request_id = _safe_text(artifact.get("request_id"))
    source_closeout_id = _safe_text(artifact.get("closeout_id"))
    reference_price = _safe_float(
        artifact.get("reference_price")
        or artifact.get("price")
        or artifact.get("entry_price"),
        0.0,
    )

    if reference_price <= 0:
        raise ValueError("reference_price is required to open a paper trade")

    quantity = round(float(size_usd) / reference_price, 8)

    result = write_trade_opened(
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        symbol=symbol,
        event_theme=event_theme,
        action_class=action_class,
        entry_price=reference_price,
        size_usd=float(size_usd),
        quantity=quantity,
        source_request_id=source_request_id or None,
        source_closeout_id=source_closeout_id or None,
        approval_required=bool(artifact.get("approval_required", True)),
        execution_allowed=bool(artifact.get("execution_allowed", False)),
        notes=notes,
        metadata={
            "source": "system_a_market_analyzer_intake",
            "source_artifact": artifact,
            "persistence_type": "trade_tracking_intake_metadata",
            "mutation_class": MUTATION_CLASS,
            "advisory_only": False,
        },
    )

    result["intake_source"] = "system_a_market_analyzer_intake"
    result["mutation_class"] = MUTATION_CLASS
    result["persistence_type"] = "trade_tracking_intake"
    result["advisory_only"] = False
    result["execution_allowed"] = False
    return result


def open_paper_trade_from_closeout(
    *,
    closeout_artifact: Dict[str, Any],
    system_id: str = "system_a",
    strategy_id: str = "market_analyzer_v1",
    size_usd: float = 10.0,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    if system_id != "system_a":
        raise ValueError("system_a_market_analyzer_intake only supports system_a")
    if strategy_id != "market_analyzer_v1":
        raise ValueError("system_a_market_analyzer_intake only supports market_analyzer_v1")

    return open_system_a_trade_from_market_analyzer(
        closeout_artifact=closeout_artifact,
        size_usd=size_usd,
        notes=notes,
    )
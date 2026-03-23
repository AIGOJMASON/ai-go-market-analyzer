from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _recommendation_row(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    item = deepcopy(recommendation)
    return {
        "symbol": item.get("symbol"),
        "sector": item.get("sector"),
        "strategy_type": item.get("strategy_type"),
        "entry_signal": item.get("entry_signal"),
        "exit_rule": item.get("exit_rule"),
        "time_horizon_hours": item.get("time_horizon_hours"),
        "market_regime": item.get("market_regime"),
        "trade_posture": item.get("trade_posture"),
        "propagation_speed": item.get("propagation_speed"),
        "ripple_depth": item.get("ripple_depth"),
        "approval_required": item.get("approval_required", True),
    }


def build_trade_recommendation_view(trade_recommendation_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the recommendations panel.

    No narrative text is added here.
    """
    packet = deepcopy(trade_recommendation_packet)
    recommendations = packet.get("recommendations", [])
    rows: List[Dict[str, Any]] = [_recommendation_row(rec) for rec in recommendations]

    return {
        "panel": "recommendations",
        "core_id": "market_analyzer_v1",
        "artifact_type": "trade_recommendation_view",
        "count": len(rows),
        "items": rows,
        "approval_gate": packet.get("approval_gate"),
        "execution_allowed": packet.get("execution_allowed", False),
        "source_artifact": packet.get("artifact_type"),
    }
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _build_single_recommendation(
    candidate: Dict[str, Any],
    regime_record: Dict[str, Any],
    propagation_record: Dict[str, Any],
    holding_window_hours: int,
) -> Dict[str, Any]:
    symbol = candidate.get("symbol")
    entry_signal = candidate.get("entry_signal", "confirmation_reclaim")
    exit_rule = candidate.get("exit_rule", "quick_exit_on_rebound_completion")

    return {
        "symbol": symbol,
        "sector": candidate.get("sector"),
        "strategy_type": "necessity_rebound_only",
        "entry_signal": entry_signal,
        "exit_rule": exit_rule,
        "time_horizon_hours": min(int(candidate.get("time_horizon_hours", holding_window_hours)), 48),
        "market_regime": regime_record.get("regime"),
        "trade_posture": regime_record.get("trade_posture"),
        "propagation_speed": propagation_record.get("propagation_speed"),
        "ripple_depth": propagation_record.get("ripple_depth"),
        "shock_origin_required": True,
        "approval_required": True,
        "narrative": None,
    }


def build_recommendations(
    validated_candidates: List[Dict[str, Any]],
    regime_record: Dict[str, Any],
    propagation_record: Dict[str, Any],
    conditioning: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build structured, non-narrative trade recommendation packets.
    """
    holding_window_hours = int(conditioning.get("holding_window_hours", 48))
    recommendations = [
        _build_single_recommendation(candidate, regime_record, propagation_record, holding_window_hours)
        for candidate in validated_candidates
    ]

    return {
        "artifact_type": "trade_recommendation_packet",
        "core_id": "market_analyzer_v1",
        "recommendations": recommendations,
        "recommendation_count": len(recommendations),
        "approval_gate": "human_trade_approval_record",
        "execution_allowed": False,
    }
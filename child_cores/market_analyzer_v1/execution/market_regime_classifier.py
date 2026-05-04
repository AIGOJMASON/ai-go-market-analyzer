from __future__ import annotations

from typing import Any, Dict


ALLOWED_REGIMES = {"normal", "volatile", "crisis"}


def classify_market_regime(market_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine market regime and participation posture.

    This module classifies only. It does not trigger trades.
    """
    volatility_level = str(market_context.get("volatility_level", "medium")).lower()
    liquidity_level = str(market_context.get("liquidity_level", "medium")).lower()
    stress_level = str(market_context.get("stress_level", "medium")).lower()

    regime = "normal"
    posture = "allowed"

    if stress_level == "high" or volatility_level == "high":
        regime = "volatile"
        posture = "restricted"

    if (stress_level == "extreme") or (volatility_level == "extreme"):
        regime = "crisis"
        posture = "conditional"

    if liquidity_level == "low" and regime == "normal":
        regime = "volatile"
        posture = "restricted"

    if regime not in ALLOWED_REGIMES:
        regime = "volatile"
        posture = "restricted"

    return {
        "artifact_type": "market_regime_record",
        "core_id": "market_analyzer_v1",
        "regime": regime,
        "trade_posture": posture,
        "volatility_level": volatility_level,
        "liquidity_level": liquidity_level,
        "stress_level": stress_level,
        "trade_allowed": posture in {"allowed", "restricted", "conditional"},
    }
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def build_market_regime_view(market_regime_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the market regime panel view.

    This is a pure presentation transform of the regime artifact.
    """
    record = deepcopy(market_regime_record)

    return {
        "panel": "market_regime",
        "core_id": "market_analyzer_v1",
        "artifact_type": "market_regime_view",
        "regime": record.get("regime"),
        "trade_posture": record.get("trade_posture"),
        "trade_allowed": record.get("trade_allowed", False),
        "volatility_level": record.get("volatility_level"),
        "liquidity_level": record.get("liquidity_level"),
        "stress_level": record.get("stress_level"),
        "source_artifact": record.get("artifact_type"),
    }
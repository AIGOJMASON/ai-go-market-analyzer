from __future__ import annotations

from typing import Any, Dict


class MarketAnalyzerHistoricalContextBridge:
    """
    Northstar-safe stub.
    External historical_market dependency removed.
    """

    def __init__(self) -> None:
        pass

    def detect_setup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "stubbed",
            "setup_detected": False,
            "confidence": 0.0,
            "reason": "historical_market dependency removed under Northstar hardening",
        }
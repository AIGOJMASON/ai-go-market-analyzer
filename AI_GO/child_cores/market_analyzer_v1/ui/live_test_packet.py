from __future__ import annotations


def build_live_test_packet() -> dict:
    return {
        "artifact_type": "pm_decision_packet",
        "dispatched_by": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "dispatch_id": "LIVE-TEST-001",
        "source": "validated_upstream",
        "receipt": {"receipt_id": "LIVE-RCPT-001"},
        "payload": {
            "conditioning": {
                "holding_window_hours": 24,
                "liquidity_preference": "high",
            },
            "market_context": {
                "volatility_level": "medium",
                "liquidity_level": "high",
                "stress_level": "medium",
            },
            "event": {
                "event_id": "EVT-LIVE-001",
                "event_type": "supply_shock",
                "propagation_speed": "fast",
                "ripple_depth": "primary",
                "shock_confirmed": True,
            },
            "macro_bias": {
                "direction": "neutral",
            },
            "candidates": [
                {
                    "symbol": "XLE",
                    "sector": "energy",
                    "liquidity": "high",
                    "stabilization": True,
                    "reclaim": True,
                    "confirmation": True,
                    "entry_signal": "confirmation_reclaim",
                    "exit_rule": "quick_exit_on_rebound_completion",
                    "time_horizon_hours": 24,
                },
                {
                    "symbol": "NTR",
                    "sector": "fertilizer",
                    "liquidity": "medium",
                    "stabilization": True,
                    "reclaim": True,
                    "confirmation": True,
                    "time_horizon_hours": 36,
                },
            ],
        },
    }
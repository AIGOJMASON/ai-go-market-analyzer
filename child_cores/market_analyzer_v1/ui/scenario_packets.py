from __future__ import annotations


def scenario_01_valid_energy_rebound() -> dict:
    return {
        "scenario_id": "SCN-01",
        "name": "valid_energy_rebound",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-01-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-01-RCPT"},
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
                    "event_id": "SCN-01-EVT",
                    "event_type": "energy_supply_shock",
                    "propagation_speed": "fast",
                    "ripple_depth": "primary",
                    "shock_confirmed": True,
                },
                "macro_bias": {"direction": "neutral"},
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
                    }
                ],
            },
        },
    }


def scenario_02_non_necessity_rejected() -> dict:
    return {
        "scenario_id": "SCN-02",
        "name": "non_necessity_rejected",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-02-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-02-RCPT"},
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
                    "event_id": "SCN-02-EVT",
                    "event_type": "market_drop",
                    "propagation_speed": "fast",
                    "ripple_depth": "primary",
                    "shock_confirmed": True,
                },
                "macro_bias": {"direction": "neutral"},
                "candidates": [
                    {
                        "symbol": "TSLA",
                        "sector": "automotive",
                        "liquidity": "high",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                    }
                ],
            },
        },
    }


def scenario_03_missing_confirmation_rejected() -> dict:
    return {
        "scenario_id": "SCN-03",
        "name": "missing_confirmation_rejected",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-03-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-03-RCPT"},
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
                    "event_id": "SCN-03-EVT",
                    "event_type": "fertilizer_disruption",
                    "propagation_speed": "medium",
                    "ripple_depth": "secondary",
                    "shock_confirmed": True,
                },
                "macro_bias": {"direction": "neutral"},
                "candidates": [
                    {
                        "symbol": "NTR",
                        "sector": "fertilizer",
                        "liquidity": "medium",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": False,
                    }
                ],
            },
        },
    }


def scenario_04_crisis_regime_still_structured() -> dict:
    return {
        "scenario_id": "SCN-04",
        "name": "crisis_regime_structured_output",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-04-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-04-RCPT"},
            "payload": {
                "conditioning": {
                    "holding_window_hours": 12,
                    "liquidity_preference": "high",
                },
                "market_context": {
                    "volatility_level": "extreme",
                    "liquidity_level": "high",
                    "stress_level": "extreme",
                },
                "event": {
                    "event_id": "SCN-04-EVT",
                    "event_type": "critical_infrastructure_shock",
                    "propagation_speed": "fast",
                    "ripple_depth": "primary",
                    "shock_confirmed": True,
                },
                "macro_bias": {"direction": "defensive"},
                "candidates": [
                    {
                        "symbol": "PAVE",
                        "sector": "infrastructure",
                        "liquidity": "high",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                        "time_horizon_hours": 12,
                    }
                ],
            },
        },
    }


def scenario_05_mixed_candidate_set_filters_correctly() -> dict:
    return {
        "scenario_id": "SCN-05",
        "name": "mixed_candidate_set_filters_correctly",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-05-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-05-RCPT"},
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
                    "event_id": "SCN-05-EVT",
                    "event_type": "chip_supply_shock",
                    "propagation_speed": "medium",
                    "ripple_depth": "secondary",
                    "shock_confirmed": True,
                },
                "macro_bias": {"direction": "neutral"},
                "candidates": [
                    {
                        "symbol": "SMH",
                        "sector": "critical_technology",
                        "liquidity": "high",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                        "time_horizon_hours": 24,
                    }
                ],
            },
        },
    }


def scenario_06_unconfirmed_shock_rejected() -> dict:
    return {
        "scenario_id": "SCN-06",
        "name": "unconfirmed_shock_rejected",
        "packet": {
            "artifact_type": "pm_decision_packet",
            "dispatched_by": "PM_CORE",
            "target_core": "market_analyzer_v1",
            "dispatch_id": "SCN-06-DISPATCH",
            "source": "validated_upstream",
            "receipt": {"receipt_id": "SCN-06-RCPT"},
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
                    "event_id": "SCN-06-EVT",
                    "event_type": "rumor_event",
                    "propagation_speed": "fast",
                    "ripple_depth": "primary",
                    "shock_confirmed": False,
                },
                "macro_bias": {"direction": "neutral"},
                "candidates": [
                    {
                        "symbol": "XLE",
                        "sector": "energy",
                        "liquidity": "high",
                        "stabilization": True,
                        "reclaim": True,
                        "confirmation": True,
                    }
                ],
            },
        },
    }


def all_scenarios():
    return [
        scenario_01_valid_energy_rebound(),
        scenario_02_non_necessity_rejected(),
        scenario_03_missing_confirmation_rejected(),
        scenario_04_crisis_regime_still_structured(),
        scenario_05_mixed_candidate_set_filters_correctly(),
        scenario_06_unconfirmed_shock_rejected(),
    ]
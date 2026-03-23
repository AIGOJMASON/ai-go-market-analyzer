from __future__ import annotations

from copy import deepcopy

from AI_GO.child_cores.market_analyzer_v1.ui.live_test_packet import build_live_test_packet


def _packet(
    dispatch_id: str,
    receipt_id: str,
    event_id: str,
) -> dict:
    """
    Start from the known-good live packet contract so replay packets inherit
    whatever exact shape the local runtime already accepts.
    """
    packet = deepcopy(build_live_test_packet())
    packet["dispatch_id"] = dispatch_id
    packet["receipt"]["receipt_id"] = receipt_id

    payload = packet.setdefault("payload", {})
    event = payload.setdefault("event", {})
    event["event_id"] = event_id
    return packet


def build_historical_replay_packets() -> list[dict]:
    packets: list[dict] = []

    # HR-01: necessity-qualified energy rebound after confirmed shock.
    p1 = _packet(
        dispatch_id="HIST-REPLAY-001",
        receipt_id="HIST-RCPT-001",
        event_id="EVT-HIST-001",
    )
    p1["payload"]["market_context"] = {
        "volatility_level": "high",
        "liquidity_level": "high",
        "stress_level": "high",
    }
    p1["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "primary",
            "shock_confirmed": True,
        }
    )
    p1["payload"]["candidates"] = [
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
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 36,
        },
    ]
    packets.append(p1)

    # HR-02: non-necessity candidates should produce no recommendation.
    p2 = _packet(
        dispatch_id="HIST-REPLAY-002",
        receipt_id="HIST-RCPT-002",
        event_id="EVT-HIST-002",
    )
    p2["payload"]["market_context"] = {
        "volatility_level": "medium",
        "liquidity_level": "high",
        "stress_level": "low",
    }
    p2["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "primary",
            "shock_confirmed": True,
        }
    )
    p2["payload"]["candidates"] = [
        {
            "symbol": "ARKK",
            "sector": "speculative_growth",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
        {
            "symbol": "SOXX",
            "sector": "semiconductors",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
    ]
    packets.append(p2)

    # HR-03: domain theme present, but no confirmation.
    p3 = _packet(
        dispatch_id="HIST-REPLAY-003",
        receipt_id="HIST-RCPT-003",
        event_id="EVT-HIST-003",
    )
    p3["payload"]["market_context"] = {
        "volatility_level": "high",
        "liquidity_level": "high",
        "stress_level": "medium",
    }
    p3["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "primary",
            "shock_confirmed": True,
        }
    )
    p3["payload"]["candidates"] = [
        {
            "symbol": "XLE",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": False,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
        {
            "symbol": "CVX",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": False,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
    ]
    packets.append(p3)

    # HR-04: crisis regime still structured and execution-blocked.
    p4 = _packet(
        dispatch_id="HIST-REPLAY-004",
        receipt_id="HIST-RCPT-004",
        event_id="EVT-HIST-004",
    )
    p4["payload"]["conditioning"] = {
        "holding_window_hours": 12,
        "liquidity_preference": "high",
    }
    p4["payload"]["market_context"] = {
        "volatility_level": "high",
        "liquidity_level": "medium",
        "stress_level": "high",
    }
    p4["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "cross_sector",
            "shock_confirmed": True,
        }
    )
    p4["payload"]["candidates"] = [
        {
            "symbol": "XLE",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 12,
        },
        {
            "symbol": "SLV",
            "sector": "metals",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 12,
        },
    ]
    packets.append(p4)

    # HR-05: mixed candidate set; only valid necessity names should survive.
    p5 = _packet(
        dispatch_id="HIST-REPLAY-005",
        receipt_id="HIST-RCPT-005",
        event_id="EVT-HIST-005",
    )
    p5["payload"]["market_context"] = {
        "volatility_level": "medium",
        "liquidity_level": "high",
        "stress_level": "medium",
    }
    p5["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "primary",
            "shock_confirmed": True,
        }
    )
    p5["payload"]["candidates"] = [
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
            "symbol": "CORN",
            "sector": "agriculture",
            "liquidity": "medium",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
        {
            "symbol": "QQQ",
            "sector": "tech",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": True,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
        {
            "symbol": "CVX",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": False,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
    ]
    packets.append(p5)

    # HR-06: still a shock packet, but candidates fail confirmation.
    # This avoids violating the runtime's hard requirement for shock flow.
    p6 = _packet(
        dispatch_id="HIST-REPLAY-006",
        receipt_id="HIST-RCPT-006",
        event_id="EVT-HIST-006",
    )
    p6["payload"]["market_context"] = {
        "volatility_level": "high",
        "liquidity_level": "high",
        "stress_level": "high",
    }
    p6["payload"]["event"].update(
        {
            "event_type": "supply_shock",
            "propagation_speed": "fast",
            "ripple_depth": "primary",
            "shock_confirmed": True,
        }
    )
    p6["payload"]["candidates"] = [
        {
            "symbol": "XLE",
            "sector": "energy",
            "liquidity": "high",
            "stabilization": True,
            "reclaim": True,
            "confirmation": False,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
        {
            "symbol": "WEAT",
            "sector": "agriculture",
            "liquidity": "medium",
            "stabilization": True,
            "reclaim": True,
            "confirmation": False,
            "entry_signal": "confirmation_reclaim",
            "exit_rule": "quick_exit_on_rebound_completion",
            "time_horizon_hours": 24,
        },
    ]
    packets.append(p6)

    return packets


def clone_replay_packets() -> list[dict]:
    return deepcopy(build_historical_replay_packets())
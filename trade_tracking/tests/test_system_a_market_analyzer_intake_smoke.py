from __future__ import annotations

from AI_GO.trade_tracking.system_a_market_analyzer_intake import evaluate_system_a_trade_open


def run() -> None:
    closeout_artifact = {
        "closeout_status": "accepted",
        "request_id": "system-a-smoke-001",
        "closeout_id": "closeout_system_a_smoke_001",
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "reference_price": 58.05,
        "approval_required": True,
        "execution_allowed": False,
        "watchlist_panel": {
            "posture_label": "constructive",
            "no_trade_state": {
                "is_no_trade": False,
                "reason": None,
            },
            "formal_score": 0.72,
        },
    }

    result = evaluate_system_a_trade_open(
        closeout_artifact=closeout_artifact,
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        size_usd=10.0,
    )
    print(result)


if __name__ == "__main__":
    run()
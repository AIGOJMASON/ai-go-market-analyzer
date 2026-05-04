from __future__ import annotations

from AI_GO.trade_tracking.trade_intake_from_closeout import open_paper_trade_from_closeout


def run() -> None:
    closeout_artifact = {
        "request_id": "closeout-smoke-001",
        "closeout_id": "closeout_smoke_001",
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "reference_price": 58.05,
        "approval_required": True,
        "execution_allowed": False,
    }
    result = open_paper_trade_from_closeout(
        closeout_artifact=closeout_artifact,
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        size_usd=10.0,
        notes="smoke intake from closeout",
    )
    print(result)


if __name__ == "__main__":
    run()
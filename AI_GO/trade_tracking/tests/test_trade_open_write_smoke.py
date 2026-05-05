from __future__ import annotations

from AI_GO.trade_tracking.trade_writer import write_trade_opened


def run() -> None:
    result = write_trade_opened(
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        symbol="XLE",
        event_theme="energy_rebound",
        action_class="long",
        entry_price=58.05,
        size_usd=10.0,
        quantity=round(10.0 / 58.05, 8),
        source_request_id="smoke-open-001",
        notes="smoke open",
    )
    print(result)


if __name__ == "__main__":
    run()
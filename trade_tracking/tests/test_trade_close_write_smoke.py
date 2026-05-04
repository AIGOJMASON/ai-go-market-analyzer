from __future__ import annotations

from AI_GO.trade_tracking.trade_writer import write_trade_closed, write_trade_opened


def run() -> None:
    opened = write_trade_opened(
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        symbol="XLE",
        event_theme="energy_rebound",
        action_class="long",
        entry_price=58.05,
        size_usd=10.0,
        quantity=round(10.0 / 58.05, 8),
        source_request_id="smoke-close-001",
        notes="smoke open before close",
    )

    trade_id = opened["event_record"]["trade_id"]

    closed = write_trade_closed(
        system_id="system_a",
        strategy_id="market_analyzer_v1",
        trade_id=trade_id,
        symbol="XLE",
        event_theme="energy_rebound",
        action_class="long",
        exit_price=59.10,
        realized_pnl_usd=0.18,
        hold_duration_seconds=3600,
        close_reason="smoke_target_hit",
        source_request_id="smoke-close-001",
        notes="smoke close",
    )
    print(closed)


if __name__ == "__main__":
    run()
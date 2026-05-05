from __future__ import annotations

from AI_GO.trade_tracking.performance.performance_state_writer import write_latest_performance_summary


def run() -> None:
    result = write_latest_performance_summary(system_id="system_a")
    print(result)


if __name__ == "__main__":
    run()
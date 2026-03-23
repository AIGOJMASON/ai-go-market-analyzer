from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.historical_replay_runner import (
    run_historical_replay,
)


def _render_result(item: dict, index: int) -> str:
    lines: list[str] = []
    case_id = f"[HR-{index:02d}] {item.get('case', 'unknown_case')}"

    lines.append(case_id)
    lines.append(f"status: {item.get('status')}")
    lines.append(f"dispatch_id: {item.get('dispatch_id')}")
    lines.append(f"should_succeed: {item.get('should_succeed')}")
    lines.append(f"actual_success: {item.get('actual_success')}")
    lines.append(f"recommendation_count: {item.get('recommendation_count')}")
    lines.append(f"watcher_passed: {item.get('watcher_passed')}")
    lines.append(f"execution_allowed: {item.get('execution_allowed')}")
    lines.append(f"recommendation_symbols: {item.get('recommendation_symbols', [])}")

    errors = item.get("errors") or []
    if errors:
        lines.append("errors:")
        for error in errors:
            lines.append(f"  - {error}")

    return "\n".join(lines)


def render_historical_replay_report(result: dict) -> str:
    lines: list[str] = []
    lines.append("MARKET_ANALYZER_V1 HISTORICAL REPLAY REPORT")
    lines.append(f"passed: {result.get('passed', 0)}")
    lines.append(f"failed: {result.get('failed', 0)}")
    lines.append("")

    for index, item in enumerate(result.get("results", []), start=1):
        lines.append(_render_result(item, index))
        lines.append("")

    return "\n".join(lines).rstrip()


def main() -> None:
    result = run_historical_replay()
    report = render_historical_replay_report(result)
    print(report)


if __name__ == "__main__":
    main()
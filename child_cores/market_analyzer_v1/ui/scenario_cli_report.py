from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.child_cores.market_analyzer_v1.ui.scenario_runner import run_all_scenarios


def render_scenario_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("MARKET_ANALYZER_V1 SCENARIO REPORT")
    lines.append(f"passed: {report.get('passed')}")
    lines.append(f"failed: {report.get('failed')}")

    for item in report.get("results", []):
        lines.append("")
        lines.append(f"[{item.get('scenario_id')}] {item.get('name')}")
        lines.append(f"status: {item.get('status')}")
        lines.append(f"should_succeed: {item.get('should_succeed')}")
        lines.append(f"actual_success: {item.get('actual_success')}")

        if item.get("actual_success"):
            lines.append(f"recommendation_count: {item.get('recommendation_count')}")
            lines.append(f"regime: {item.get('regime')}")
            lines.append(f"trade_posture: {item.get('trade_posture')}")
            lines.append(f"watcher_passed: {item.get('watcher_passed')}")
            lines.append(f"recommendation_symbols: {item.get('recommendation_symbols')}")
        else:
            lines.append(f"error: {item.get('error')}")

        lines.append(f"notes: {item.get('notes')}")

    return "\n".join(lines)


def main() -> None:
    report = run_all_scenarios()
    print(render_scenario_report(report))


if __name__ == "__main__":
    main()
from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.child_cores.market_analyzer_v1.execution.run import (
    MarketAnalyzerRuntimeError,
    run,
)
from AI_GO.child_cores.market_analyzer_v1.outputs.output_builder import build_output_views
from AI_GO.child_cores.market_analyzer_v1.ui.scenario_expectations import SCENARIO_EXPECTATIONS
from AI_GO.child_cores.market_analyzer_v1.ui.scenario_packets import all_scenarios
from AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher import verify_runtime_result


def evaluate_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    scenario_id = scenario["scenario_id"]
    name = scenario["name"]
    packet = scenario["packet"]
    expectation = SCENARIO_EXPECTATIONS[scenario_id]

    try:
        runtime_result = run(packet)
        watcher_result = verify_runtime_result(runtime_result)
        dashboard_output = build_output_views(runtime_result)

        recommendations = runtime_result["artifacts"]["trade_recommendation_packet"]["recommendations"]
        recommendation_count = runtime_result["artifacts"]["trade_recommendation_packet"]["recommendation_count"]
        regime = runtime_result["artifacts"]["market_regime_record"]["regime"]
        trade_posture = runtime_result["artifacts"]["market_regime_record"]["trade_posture"]

        passed = (
            expectation["should_succeed"] is True
            and recommendation_count == expectation["expected_recommendation_count"]
            and regime == expectation["expected_regime"]
            and trade_posture == expectation["expected_trade_posture"]
            and watcher_result.get("watcher_passed") is True
        )

        return {
            "scenario_id": scenario_id,
            "name": name,
            "status": "passed" if passed else "failed",
            "should_succeed": True,
            "actual_success": True,
            "recommendation_count": recommendation_count,
            "regime": regime,
            "trade_posture": trade_posture,
            "watcher_passed": watcher_result.get("watcher_passed", False),
            "recommendation_symbols": [item.get("symbol") for item in recommendations],
            "notes": expectation.get("notes"),
            "dashboard_artifact_type": dashboard_output.get("artifact_type"),
        }

    except MarketAnalyzerRuntimeError as exc:
        message = str(exc)
        passed = (
            expectation["should_succeed"] is False
            and expectation["expected_error_contains"] in message
        )

        return {
            "scenario_id": scenario_id,
            "name": name,
            "status": "passed" if passed else "failed",
            "should_succeed": False,
            "actual_success": False,
            "error": message,
            "notes": expectation.get("notes"),
        }


def run_all_scenarios() -> Dict[str, Any]:
    results = [evaluate_scenario(item) for item in all_scenarios()]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "core_id": "market_analyzer_v1",
        "artifact_type": "scenario_run_report",
        "passed": passed,
        "failed": failed,
        "results": results,
    }


def main() -> None:
    report = run_all_scenarios()
    print(report)


if __name__ == "__main__":
    main()
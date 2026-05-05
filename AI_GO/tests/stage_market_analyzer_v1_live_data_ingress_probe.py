from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import run_live_case


def main() -> None:
    results = []

    positive = run_live_case("LIVE-DATA-001")
    positive_packet = positive["normalized_packet"]
    positive_result = positive["routed_result"]

    results.append(
        {
            "case": "case_01_positive_packet_targets_market_analyzer",
            "status": "passed" if positive_packet["target_core"] == "market_analyzer_v1" else "failed",
        }
    )
    results.append(
        {
            "case": "case_02_positive_parent_authority_is_pm_core",
            "status": "passed" if positive_packet["parent_authority"] == "PM_CORE" else "failed",
        }
    )
    results.append(
        {
            "case": "case_03_positive_execution_block_preserved",
            "status": "passed" if positive_packet["execution_allowed"] is False else "failed",
        }
    )
    results.append(
        {
            "case": "case_04_positive_case_reaches_ok_status",
            "status": "passed" if positive_result.get("status") == "ok" else "failed",
        }
    )
    results.append(
        {
            "case": "case_05_positive_case_watcher_passes",
            "status": "passed" if positive_result.get("watcher", {}).get("passed") is True else "failed",
        }
    )
    results.append(
        {
            "case": "case_06_positive_case_has_recommendation",
            "status": "passed"
            if positive_result.get("trade_recommendation_packet", {}).get("recommendation_count", 0) >= 1
            else "failed",
        }
    )

    negative = run_live_case("LIVE-DATA-002")
    negative_result = negative["routed_result"]

    results.append(
        {
            "case": "case_07_negative_case_rejects",
            "status": "passed" if negative_result.get("status") == "rejected" else "failed",
        }
    )
    results.append(
        {
            "case": "case_08_negative_case_preserves_execution_block",
            "status": "passed" if negative_result.get("execution_allowed") is False else "failed",
        }
    )
    results.append(
        {
            "case": "case_09_negative_case_has_no_recommendations",
            "status": "passed" if not negative_result.get("recommendations", []) else "failed",
        }
    )
    results.append(
        {
            "case": "case_10_route_mode_recorded",
            "status": "passed" if positive.get("route_mode") in {"pm_route", "fallback_stub"} else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = len(results) - passed

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()
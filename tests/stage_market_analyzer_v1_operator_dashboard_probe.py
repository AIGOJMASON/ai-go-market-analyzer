from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner import run_operator_dashboard


def main() -> None:
    results = []

    positive = run_operator_dashboard("LIVE-DATA-001")["dashboard"]
    negative = run_operator_dashboard("LIVE-DATA-002")["dashboard"]

    results.append(
        {
            "case": "case_01_dashboard_type_present",
            "status": "passed"
            if positive.get("dashboard_type") == "market_analyzer_v1_operator_dashboard"
            else "failed",
        }
    )
    results.append(
        {
            "case": "case_02_market_panel_present",
            "status": "passed" if "market_panel" in positive else "failed",
        }
    )
    results.append(
        {
            "case": "case_03_candidate_panel_present",
            "status": "passed" if "candidate_panel" in positive else "failed",
        }
    )
    results.append(
        {
            "case": "case_04_recommendation_panel_present",
            "status": "passed" if "recommendation_panel" in positive else "failed",
        }
    )
    results.append(
        {
            "case": "case_05_governance_panel_present",
            "status": "passed" if "governance_panel" in positive else "failed",
        }
    )
    results.append(
        {
            "case": "case_06_positive_dashboard_watcher_passes",
            "status": "passed"
            if positive["governance_panel"]["watcher_passed"] is True
            else "failed",
        }
    )
    results.append(
        {
            "case": "case_07_positive_dashboard_approval_required",
            "status": "passed"
            if positive["governance_panel"]["approval_required"] is True
            else "failed",
        }
    )
    results.append(
        {
            "case": "case_08_positive_dashboard_execution_blocked",
            "status": "passed"
            if positive["governance_panel"]["execution_allowed"] is False
            else "failed",
        }
    )
    results.append(
        {
            "case": "case_09_negative_dashboard_rejection_surface_present",
            "status": "passed"
            if negative["rejection_panel"]["rejected"] is True
            else "failed",
        }
    )
    results.append(
        {
            "case": "case_10_negative_dashboard_has_zero_recommendations",
            "status": "passed"
            if negative["recommendation_panel"]["recommendation_count"] == 0
            else "failed",
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
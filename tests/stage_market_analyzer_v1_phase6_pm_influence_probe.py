from __future__ import annotations

from AI_GO.api.pm_influence import build_pm_influence_record
from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner import (
    run_operator_dashboard,
)


def _base_routed_result():
    return {
        "status": "ok",
        "request_id": "phase6-001",
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "case_panel": {
            "case_id": "LIVE-DATA-001",
            "title": "Chile supply event",
            "observed_at": "2026-03-24T09:00:00Z",
        },
        "market_panel": {
            "market_regime": "normal",
            "event_theme": "supply_expansion",
            "macro_bias": "mixed",
            "headline": "New Chile copper mine opening announced",
        },
        "candidate_panel": {
            "candidate_count": 1,
            "symbols": ["COPX"],
        },
        "recommendation_panel": {
            "recommendation_count": 1,
            "recommendations": [
                {
                    "symbol": "COPX",
                    "entry": "wait for confirmation",
                    "exit": "first failed rebound",
                    "confidence": "medium",
                }
            ],
        },
        "governance_panel": {
            "watcher_passed": True,
            "approval_required": True,
        },
        "rejection_panel": {
            "rejected": False,
            "reason": None,
        },
    }


def _refinement_packets_confidence_reduction():
    return [
        {
            "signal": "historical_overreaction_pattern",
            "visible_insight": "Historical supply expansion events often show delayed price impact and early reversals.",
            "impact": "confidence_reduction",
            "confidence_adjustment": "down",
            "authority": "refinement_influence",
            "source": "refinement",
        }
    ]


def _refinement_packets_annotation_only():
    return [
        {
            "signal": "historical_context_present",
            "visible_insight": "Historical analogs suggest slower confirmation is more reliable than immediate reaction.",
            "impact": "annotation_only",
            "authority": "refinement_influence",
            "source": "refinement",
        }
    ]


def run_probe():
    results = []

    base_result = _base_routed_result()

    influence_record = build_pm_influence_record(
        core_id="market_analyzer_v1",
        recommendation_panel=base_result["recommendation_panel"],
        refinement_packets=_refinement_packets_confidence_reduction(),
    )

    recommendation = influence_record["recommendation_panel"]["recommendations"][0]
    results.append(
        {
            "case": "case_01_confidence_reduction_is_bounded",
            "status": "passed"
            if recommendation["base_confidence"] == "medium"
            and recommendation["display_confidence"] == "low"
            else "failed",
        }
    )

    results.append(
        {
            "case": "case_02_entry_and_exit_not_mutated",
            "status": "passed"
            if recommendation["entry"] == "wait for confirmation"
            and recommendation["exit"] == "first failed rebound"
            else "failed",
        }
    )

    dashboard = run_operator_dashboard(
        routed_result=base_result,
        refinement_packets=_refinement_packets_confidence_reduction(),
    )
    results.append(
        {
            "case": "case_03_dashboard_contains_visible_refinement_panel",
            "status": "passed"
            if dashboard["refinement_panel"]["visible"] is True
            and len(dashboard["refinement_panel"]["insights"]) == 1
            else "failed",
        }
    )

    annotation_dashboard = run_operator_dashboard(
        routed_result=base_result,
        refinement_packets=_refinement_packets_annotation_only(),
    )
    ann_rec = annotation_dashboard["recommendation_panel"]["recommendations"][0]
    results.append(
        {
            "case": "case_04_annotation_only_does_not_change_display_confidence",
            "status": "passed"
            if ann_rec["display_confidence"] == "medium"
            else "failed",
        }
    )

    zero_dashboard = run_operator_dashboard(
        routed_result=base_result,
        refinement_packets=[],
    )
    results.append(
        {
            "case": "case_05_zero_refinement_packets_keep_output_stable",
            "status": "passed"
            if zero_dashboard["refinement_panel"]["visible"] is False
            and zero_dashboard["recommendation_panel"]["recommendations"][0]["display_confidence"] == "medium"
            else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
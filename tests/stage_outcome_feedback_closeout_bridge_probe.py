from __future__ import annotations

from AI_GO.core.outcome_feedback.closeout_outcome_feedback_bridge import (
    record_outcome_feedback_from_closeout,
)


def _build_accepted_closeout_artifact():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260331T230500Z_probe",
        "closeout_status": "accepted",
        "runtime_panel": {
            "event_theme": "energy_rebound",
        },
    }


def _build_failed_closeout_artifact():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260331T230500Z_probe_fail",
        "closeout_status": "failed",
        "runtime_panel": {
            "event_theme": "energy_rebound",
        },
    }


def _build_observed_outcome_view():
    return {
        "actual_outcome": "confirmed energy rebound after follow-through buying",
        "notes": "Bridge probe observed a matching outcome",
        "source": "manual",
    }


def run_probe():
    accepted_result = record_outcome_feedback_from_closeout(
        closeout_artifact=_build_accepted_closeout_artifact(),
        observed_outcome_view=_build_observed_outcome_view(),
        core_id="market_analyzer_v1",
    )

    failed_result = record_outcome_feedback_from_closeout(
        closeout_artifact=_build_failed_closeout_artifact(),
        observed_outcome_view=_build_observed_outcome_view(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_accepted_closeout_bridge_records_outcome_feedback",
        "status": "passed" if accepted_result.get("status") == "recorded" else "failed",
    })

    results.append({
        "case": "case_02_failed_closeout_bridge_rejected",
        "status": "passed" if failed_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_expected_behavior_derived_from_closeout",
        "status": "passed" if accepted_result.get("expected_behavior") == "energy rebound" else "failed",
    })

    results.append({
        "case": "case_04_index_entry_written",
        "status": "passed" if accepted_result.get("index_status") == "indexed" else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
from __future__ import annotations

from AI_GO.core.outcome_feedback.outcome_feedback_record import (
    record_outcome_feedback,
)


def _build_accepted_closeout_record():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260331T220500Z_probe",
        "closeout_status": "accepted",
    }


def _build_failed_closeout_record():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260331T220500Z_probe_fail",
        "closeout_status": "failed",
    }


def _build_outcome_view():
    return {
        "expected_behavior": "energy rebound",
        "actual_outcome": "confirmed energy rebound after follow-through buying",
        "notes": "Probe outcome matched expected direction",
        "source": "manual",
    }


def run_probe():
    accepted_result = record_outcome_feedback(
        closeout_record=_build_accepted_closeout_record(),
        outcome_view=_build_outcome_view(),
        core_id="market_analyzer_v1",
    )

    failed_result = record_outcome_feedback(
        closeout_record=_build_failed_closeout_record(),
        outcome_view=_build_outcome_view(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_accepted_closeout_records_outcome_feedback",
        "status": "passed" if accepted_result.get("status") == "recorded" else "failed",
    })

    results.append({
        "case": "case_02_failed_closeout_rejected",
        "status": "passed" if failed_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_outcome_class_present",
        "status": "passed" if accepted_result.get("outcome_class") else "failed",
    })

    results.append({
        "case": "case_04_confidence_delta_present",
        "status": "passed" if accepted_result.get("confidence_delta") else "failed",
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
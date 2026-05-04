from __future__ import annotations

from AI_GO.core.visibility.correctness_visibility_builder import (
    build_correctness_visibility_artifact,
)


def _build_outcome_feedback_record():
    return {
        "recorded_at": "2026-03-31T23:55:00Z",
        "status": "recorded",
        "annotation_only": True,
        "core_id": "market_analyzer_v1",
        "closeout_id": "closeout_market_analyzer_v1_20260331T235500Z_probe",
        "closeout_status": "accepted",
        "expected_behavior": "energy rebound",
        "actual_outcome": "confirmed energy rebound after follow-through buying",
        "outcome_class": "confirmed",
        "confidence_delta": "up",
        "source": "manual",
    }


def _build_outcome_feedback_index():
    return {
        "generated_at": "2026-03-31T23:56:00Z",
        "entry_count": 5,
        "latest_entry_id": "outcome_feedback_market_analyzer_v1_closeout_market_analyzer_v1_20260331T235500Z_probe",
        "entries": [],
    }


def _build_refinement_packet():
    return {
        "generated_at": "2026-03-31T23:57:00Z",
        "status": "generated",
        "annotation_only": True,
        "core_id": "market_analyzer_v1",
        "refinement_signal": {
            "refinement_posture": "reinforce",
            "confidence_posture": "strengthen",
            "summary": "Outcome matched expectation",
        },
    }


def _build_pm_intake_record():
    return {
        "generated_at": "2026-03-31T23:58:00Z",
        "status": "generated",
        "annotation_only": True,
        "core_id": "market_analyzer_v1",
        "pm_signal": {
            "pm_awareness_posture": "reinforced_support",
            "summary": "Outcome-derived refinement reinforces support posture",
        },
    }


def _build_rejected_pm_intake_record():
    return {
        "status": "rejected",
        "annotation_only": True,
        "pm_signal": {},
    }


def run_probe():
    generated_result = build_correctness_visibility_artifact(
        outcome_feedback_record=_build_outcome_feedback_record(),
        outcome_feedback_index=_build_outcome_feedback_index(),
        refinement_packet=_build_refinement_packet(),
        pm_intake_record=_build_pm_intake_record(),
        core_id="market_analyzer_v1",
    )

    rejected_result = build_correctness_visibility_artifact(
        outcome_feedback_record=_build_outcome_feedback_record(),
        outcome_feedback_index=_build_outcome_feedback_index(),
        refinement_packet=_build_refinement_packet(),
        pm_intake_record=_build_rejected_pm_intake_record(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_valid_inputs_generate_correctness_visibility_artifact",
        "status": "passed" if generated_result.get("status") == "generated" else "failed",
    })

    results.append({
        "case": "case_02_invalid_pm_input_rejected",
        "status": "passed" if rejected_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_latest_outcome_class_preserved",
        "status": "passed"
        if generated_result.get("correctness_summary", {}).get("latest_outcome_class") == "confirmed"
        else "failed",
    })

    results.append({
        "case": "case_04_history_count_preserved",
        "status": "passed"
        if generated_result.get("history_view", {}).get("entry_count") == 5
        else "failed",
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
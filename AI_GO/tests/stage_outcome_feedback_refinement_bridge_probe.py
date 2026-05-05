from __future__ import annotations

from AI_GO.core.refinement.outcome_feedback_refinement_bridge import (
    build_outcome_feedback_refinement_packet,
)


def _build_recorded_outcome_feedback_record():
    return {
        "recorded_at": "2026-03-31T23:30:00Z",
        "status": "recorded",
        "annotation_only": True,
        "core_id": "market_analyzer_v1",
        "closeout_id": "closeout_market_analyzer_v1_20260331T233000Z_probe",
        "closeout_status": "accepted",
        "expected_behavior": "energy rebound",
        "actual_outcome": "confirmed energy rebound after follow-through buying",
        "outcome_class": "confirmed",
        "confidence_delta": "up",
        "notes": "Probe outcome matched expected direction",
        "source": "manual",
    }


def _build_unrecorded_outcome_feedback_record():
    return {
        "status": "rejected",
        "annotation_only": True,
        "outcome_class": "failed",
    }


def _build_outcome_feedback_index():
    return {
        "generated_at": "2026-03-31T23:31:00Z",
        "entry_count": 3,
        "latest_entry_id": "outcome_feedback_market_analyzer_v1_closeout_market_analyzer_v1_20260331T233000Z_probe",
        "entries": [],
    }


def run_probe():
    recorded_result = build_outcome_feedback_refinement_packet(
        outcome_feedback_record=_build_recorded_outcome_feedback_record(),
        outcome_feedback_index=_build_outcome_feedback_index(),
        core_id="market_analyzer_v1",
    )

    rejected_result = build_outcome_feedback_refinement_packet(
        outcome_feedback_record=_build_unrecorded_outcome_feedback_record(),
        outcome_feedback_index=_build_outcome_feedback_index(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_recorded_outcome_feedback_generates_refinement_packet",
        "status": "passed" if recorded_result.get("status") == "generated" else "failed",
    })

    results.append({
        "case": "case_02_unrecorded_outcome_feedback_rejected",
        "status": "passed" if rejected_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_confirmed_outcome_maps_to_reinforce",
        "status": "passed"
        if recorded_result.get("refinement_signal", {}).get("refinement_posture") == "reinforce"
        else "failed",
    })

    results.append({
        "case": "case_04_index_context_preserved",
        "status": "passed"
        if recorded_result.get("index_context", {}).get("entry_count") == 3
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
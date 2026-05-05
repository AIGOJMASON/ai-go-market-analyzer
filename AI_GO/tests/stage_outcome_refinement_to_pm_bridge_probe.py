from __future__ import annotations

from AI_GO.core.refinement.outcome_refinement_to_pm_bridge import (
    build_outcome_pm_refinement_intake_record,
)


def _build_generated_outcome_feedback_refinement_packet():
    return {
        "generated_at": "2026-03-31T23:45:00Z",
        "status": "generated",
        "annotation_only": True,
        "core_id": "market_analyzer_v1",
        "source_layer": "outcome_feedback",
        "source_record": {
            "closeout_id": "closeout_market_analyzer_v1_20260331T234500Z_probe",
            "recorded_at": "2026-03-31T23:44:30Z",
            "outcome_class": "confirmed",
            "confidence_delta": "up",
            "source": "manual",
        },
        "refinement_signal": {
            "refinement_posture": "reinforce",
            "confidence_posture": "strengthen",
            "summary": "Outcome matched expectation",
            "expected_behavior": "energy rebound",
            "actual_outcome": "confirmed energy rebound after follow-through buying",
        },
        "index_context": {
            "entry_count": 4,
            "latest_entry_id": "outcome_feedback_market_analyzer_v1_closeout_market_analyzer_v1_20260331T234500Z_probe",
        },
    }


def _build_rejected_outcome_feedback_refinement_packet():
    return {
        "status": "rejected",
        "annotation_only": True,
        "refinement_signal": {
            "refinement_posture": "caution",
        },
    }


def run_probe():
    generated_result = build_outcome_pm_refinement_intake_record(
        outcome_feedback_refinement_packet=_build_generated_outcome_feedback_refinement_packet(),
        core_id="market_analyzer_v1",
    )

    rejected_result = build_outcome_pm_refinement_intake_record(
        outcome_feedback_refinement_packet=_build_rejected_outcome_feedback_refinement_packet(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_generated_outcome_refinement_packet_generates_pm_intake_record",
        "status": "passed" if generated_result.get("status") == "generated" else "failed",
    })

    results.append({
        "case": "case_02_rejected_outcome_refinement_packet_blocked",
        "status": "passed" if rejected_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_reinforce_maps_to_reinforced_support",
        "status": "passed"
        if generated_result.get("pm_signal", {}).get("pm_awareness_posture") == "reinforced_support"
        else "failed",
    })

    results.append({
        "case": "case_04_index_context_preserved",
        "status": "passed"
        if generated_result.get("index_context", {}).get("entry_count") == 4
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
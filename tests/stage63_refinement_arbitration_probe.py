from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_arbitration import (
    RefinementArbitrationError,
    build_refinement_decision_record,
)


def _scoring_record(
    candidates=None,
    sealed=True,
):
    return {
        "artifact_type": "refinement_scoring_record",
        "payload": {
            "scored_candidates": candidates
            if candidates is not None
            else [
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "accepted_intake_majority",
                    "selection_reason": "test",
                    "score_components": [],
                    "total_score": 5,
                },
                {
                    "candidate_type": "target_child_core_count",
                    "candidate_source": "counts",
                    "candidate_value": {"a": 3},
                    "selection_reason": "test",
                    "score_components": [],
                    "total_score": 4,
                },
                {
                    "candidate_type": "closeout_count",
                    "candidate_source": "counts",
                    "candidate_value": {"b": 2},
                    "selection_reason": "test",
                    "score_components": [],
                    "total_score": 3,
                },
                {
                    "candidate_type": "intake_count",
                    "candidate_source": "counts",
                    "candidate_value": {"c": 1},
                    "selection_reason": "test",
                    "score_components": [],
                    "total_score": 1,
                },
            ],
            "sealed": sealed,
        },
    }


def _expect_pass(name, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def _expect_fail(name, fn):
    try:
        fn()
        return {"case": name, "status": "failed", "error": "expected failure but passed"}
    except RefinementArbitrationError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage63_refinement_arbitration_probe():
    results = []

    # -----------------------------
    # VALID CASE
    # -----------------------------
    def case_01_valid_decision_record():
        out = build_refinement_decision_record(_scoring_record())
        assert out["artifact_type"] == "refinement_decision_record"
        assert out["payload"]["sealed"] is True

    results.append(_expect_pass("case_01_valid_decision_record", case_01_valid_decision_record))

    # -----------------------------
    # THRESHOLD LOGIC
    # -----------------------------
    def case_02_thresholds_applied_correctly():
        out = build_refinement_decision_record(_scoring_record())
        assert out["payload"]["approved_count"] >= 1
        assert out["payload"]["deferred_count"] >= 1
        assert out["payload"]["rejected_count"] >= 1

    results.append(_expect_pass("case_02_thresholds_applied_correctly", case_02_thresholds_applied_correctly))

    # -----------------------------
    # APPROVAL CAP
    # -----------------------------
    def case_03_approval_cap_enforced():
        many = _scoring_record(
            candidates=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "x",
                    "candidate_value": str(i),
                    "selection_reason": "test",
                    "score_components": [],
                    "total_score": 5,
                }
                for i in range(10)
            ]
        )
        out = build_refinement_decision_record(many)
        assert out["payload"]["approved_count"] == 3

    results.append(_expect_pass("case_03_approval_cap_enforced", case_03_approval_cap_enforced))

    # -----------------------------
    # ORDERING
    # -----------------------------
    def case_04_sorted_by_score():
        out = build_refinement_decision_record(_scoring_record())
        approved = out["payload"]["approved"]
        scores = [c["total_score"] for c in approved]
        assert scores == sorted(scores, reverse=True)

    results.append(_expect_pass("case_04_sorted_by_score", case_04_sorted_by_score))

    # -----------------------------
    # INVALID ARTIFACT TYPE
    # -----------------------------
    def case_05_reject_invalid_artifact_type():
        bad = _scoring_record()
        bad["artifact_type"] = "analytics_summary"
        build_refinement_decision_record(bad)

    results.append(_expect_fail("case_05_reject_invalid_artifact_type", case_05_reject_invalid_artifact_type))

    # -----------------------------
    # UNSEALED INPUT
    # -----------------------------
    def case_06_reject_unsealed_input():
        build_refinement_decision_record(_scoring_record(sealed=False))

    results.append(_expect_fail("case_06_reject_unsealed_input", case_06_reject_unsealed_input))

    # -----------------------------
    # MISSING FIELD
    # -----------------------------
    def case_07_reject_missing_scored_candidates():
        bad = _scoring_record()
        del bad["payload"]["scored_candidates"]
        build_refinement_decision_record(bad)

    results.append(_expect_fail("case_07_reject_missing_scored_candidates", case_07_reject_missing_scored_candidates))

    # -----------------------------
    # INTERNAL FIELD LEAK
    # -----------------------------
    def case_08_reject_internal_field_leakage():
        bad = _scoring_record()
        bad["payload"]["_internal"] = {"bad": True}
        build_refinement_decision_record(bad)

    results.append(_expect_fail("case_08_reject_internal_field_leakage", case_08_reject_internal_field_leakage))

    # -----------------------------
    # INVALID CANDIDATE STRUCTURE
    # -----------------------------
    def case_09_reject_invalid_candidate_structure():
        bad = _scoring_record(
            candidates=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "x",
                    "selection_reason": "missing_value",
                    "score_components": [],
                    "total_score": 5,
                }
            ]
        )
        build_refinement_decision_record(bad)

    results.append(_expect_fail("case_09_reject_invalid_candidate_structure", case_09_reject_invalid_candidate_structure))

    # -----------------------------
    # ZERO CANDIDATES
    # -----------------------------
    def case_10_zero_candidates_supported():
        out = build_refinement_decision_record(
            _scoring_record(candidates=[])
        )
        assert out["payload"]["approved_count"] == 0
        assert out["payload"]["deferred_count"] == 0
        assert out["payload"]["rejected_count"] == 0

    results.append(_expect_pass("case_10_zero_candidates_supported", case_10_zero_candidates_supported))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage63_refinement_arbitration_probe())
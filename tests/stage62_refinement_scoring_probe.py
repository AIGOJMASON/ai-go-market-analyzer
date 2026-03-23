from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_scoring import (
    RefinementScoringError,
    build_refinement_scoring_record,
)


def _candidate_set(
    selected_candidates=None,
    retrieval_context_included=False,
    sealed=True,
):
    return {
        "artifact_type": "refinement_candidate_set",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_INTAKE",
            "source_artifact_type": "analytics_summary",
            "retrieval_context_included": retrieval_context_included,
            "total_candidates_considered": 3 if selected_candidates is None else len(selected_candidates),
            "selected_count": 3 if selected_candidates is None else len(selected_candidates),
            "rejected_count": 0,
            "selected_candidates": selected_candidates
            if selected_candidates is not None
            else [
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "accepted_intake_majority",
                    "selection_reason": "approved_pattern_note",
                },
                {
                    "candidate_type": "closeout_count",
                    "candidate_source": "counts_by_closeout_state",
                    "candidate_value": {"closed_accepted": 2},
                    "selection_reason": "positive_count_detected",
                },
                {
                    "candidate_type": "target_child_core_count",
                    "candidate_source": "counts_by_target_child_core",
                    "candidate_value": {"proposal_saas": 5},
                    "selection_reason": "positive_count_detected",
                },
            ],
            "selection_notes": [],
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
    except RefinementScoringError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage62_refinement_scoring_probe():
    results = []

    def case_01_valid_scoring_record_from_candidate_set():
        out = build_refinement_scoring_record(_candidate_set())
        assert out["artifact_type"] == "refinement_scoring_record"
        assert out["payload"]["scored_count"] == 3
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_scoring_record_from_candidate_set",
            case_01_valid_scoring_record_from_candidate_set,
        )
    )

    def case_02_retrieval_context_adds_score_component():
        out = build_refinement_scoring_record(
            _candidate_set(retrieval_context_included=True)
        )
        first = out["payload"]["scored_candidates"][0]
        components = [item["component"] for item in first["score_components"]]
        assert "retrieval_context_present" in components

    results.append(
        _expect_pass(
            "case_02_retrieval_context_adds_score_component",
            case_02_retrieval_context_adds_score_component,
        )
    )

    def case_03_sorted_highest_score_first():
        out = build_refinement_scoring_record(_candidate_set())
        scored = out["payload"]["scored_candidates"]
        totals = [item["total_score"] for item in scored]
        assert totals == sorted(totals, reverse=True)

    results.append(
        _expect_pass(
            "case_03_sorted_highest_score_first",
            case_03_sorted_highest_score_first,
        )
    )

    def case_04_reject_unsealed_candidate_set():
        build_refinement_scoring_record(_candidate_set(sealed=False))

    results.append(
        _expect_fail(
            "case_04_reject_unsealed_candidate_set",
            case_04_reject_unsealed_candidate_set,
        )
    )

    def case_05_reject_invalid_artifact_type():
        bad = _candidate_set()
        bad["artifact_type"] = "analytics_summary"
        build_refinement_scoring_record(bad)

    results.append(
        _expect_fail(
            "case_05_reject_invalid_artifact_type",
            case_05_reject_invalid_artifact_type,
        )
    )

    def case_06_reject_missing_required_payload_field():
        bad = _candidate_set()
        del bad["payload"]["selected_candidates"]
        build_refinement_scoring_record(bad)

    results.append(
        _expect_fail(
            "case_06_reject_missing_required_payload_field",
            case_06_reject_missing_required_payload_field,
        )
    )

    def case_07_reject_internal_field_leakage():
        bad = _candidate_set()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_scoring_record(bad)

    results.append(
        _expect_fail(
            "case_07_reject_internal_field_leakage",
            case_07_reject_internal_field_leakage,
        )
    )

    def case_08_reject_invalid_candidate_type():
        bad = _candidate_set(
            selected_candidates=[
                {
                    "candidate_type": "semantic_guess",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "something",
                    "selection_reason": "bad",
                }
            ]
        )
        build_refinement_scoring_record(bad)

    results.append(
        _expect_fail(
            "case_08_reject_invalid_candidate_type",
            case_08_reject_invalid_candidate_type,
        )
    )

    def case_09_reject_invalid_count_candidate_value():
        bad = _candidate_set(
            selected_candidates=[
                {
                    "candidate_type": "closeout_count",
                    "candidate_source": "counts_by_closeout_state",
                    "candidate_value": "closed_accepted=2",
                    "selection_reason": "positive_count_detected",
                }
            ]
        )
        build_refinement_scoring_record(bad)

    results.append(
        _expect_fail(
            "case_09_reject_invalid_count_candidate_value",
            case_09_reject_invalid_count_candidate_value,
        )
    )

    def case_10_zero_candidates_supported():
        out = build_refinement_scoring_record(
            _candidate_set(selected_candidates=[])
        )
        assert out["artifact_type"] == "refinement_scoring_record"
        assert out["payload"]["scored_count"] == 0
        assert "no_candidates_to_score" in out["payload"]["scoring_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_candidates_supported",
            case_10_zero_candidates_supported,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage62_refinement_scoring_probe())
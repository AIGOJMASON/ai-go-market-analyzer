from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_promotion import (
    RefinementPromotionError,
    build_refinement_promotion_record,
)


def _decision_record(
    approved=None,
    deferred=None,
    rejected=None,
    sealed=True,
):
    return {
        "artifact_type": "refinement_decision_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_ARBITRATION",
            "source_artifact_type": "refinement_scoring_record",
            "approved_count": len(approved) if approved is not None else 2,
            "deferred_count": len(deferred) if deferred is not None else 1,
            "rejected_count": len(rejected) if rejected is not None else 1,
            "approved": approved
            if approved is not None
            else [
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "accepted_intake_majority",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "approved",
                    "decision_reason": "score_5",
                },
                {
                    "candidate_type": "target_child_core_count",
                    "candidate_source": "counts_by_target_child_core",
                    "candidate_value": {"proposal_saas": 4},
                    "selection_reason": "positive_count_detected",
                    "score_components": [],
                    "total_score": 4,
                    "decision": "approved",
                    "decision_reason": "score_4",
                },
            ],
            "deferred": deferred
            if deferred is not None
            else [
                {
                    "candidate_type": "closeout_count",
                    "candidate_source": "counts_by_closeout_state",
                    "candidate_value": {"closed_accepted": 2},
                    "selection_reason": "positive_count_detected",
                    "score_components": [],
                    "total_score": 3,
                    "decision": "deferred",
                    "decision_reason": "score_3",
                }
            ],
            "rejected": rejected
            if rejected is not None
            else [
                {
                    "candidate_type": "intake_count",
                    "candidate_source": "counts_by_intake_decision",
                    "candidate_value": {"rejected": 1},
                    "selection_reason": "positive_count_detected",
                    "score_components": [],
                    "total_score": 1,
                    "decision": "rejected",
                    "decision_reason": "score_1",
                }
            ],
            "arbitration_notes": [],
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
    except RefinementPromotionError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage64_refinement_promotion_probe():
    results = []

    def case_01_valid_promotion_record():
        out = build_refinement_promotion_record(_decision_record())
        assert out["artifact_type"] == "refinement_promotion_record"
        assert out["payload"]["promoted_count"] == 2
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_promotion_record",
            case_01_valid_promotion_record,
        )
    )

    def case_02_only_approved_items_are_promoted():
        out = build_refinement_promotion_record(_decision_record())
        promoted = out["payload"]["promoted"]
        decisions = [item["decision"] for item in promoted]
        assert decisions == ["approved", "approved"]

    results.append(
        _expect_pass(
            "case_02_only_approved_items_are_promoted",
            case_02_only_approved_items_are_promoted,
        )
    )

    def case_03_promotion_cap_enforced():
        many_approved = [
            {
                "candidate_type": "pattern_note",
                "candidate_source": "pattern_notes",
                "candidate_value": f"pattern_{i}",
                "selection_reason": "approved_pattern_note",
                "score_components": [],
                "total_score": 5,
                "decision": "approved",
                "decision_reason": "score_5",
            }
            for i in range(6)
        ]
        out = build_refinement_promotion_record(
            _decision_record(approved=many_approved, deferred=[], rejected=[])
        )
        assert out["payload"]["promoted_count"] == 3
        assert out["payload"]["overflow_not_promoted_count"] == 3
        assert "promotion_cap_enforced" in out["payload"]["promotion_notes"]

    results.append(
        _expect_pass(
            "case_03_promotion_cap_enforced",
            case_03_promotion_cap_enforced,
        )
    )

    def case_04_reject_unsealed_input():
        build_refinement_promotion_record(_decision_record(sealed=False))

    results.append(
        _expect_fail(
            "case_04_reject_unsealed_input",
            case_04_reject_unsealed_input,
        )
    )

    def case_05_reject_invalid_artifact_type():
        bad = _decision_record()
        bad["artifact_type"] = "refinement_scoring_record"
        build_refinement_promotion_record(bad)

    results.append(
        _expect_fail(
            "case_05_reject_invalid_artifact_type",
            case_05_reject_invalid_artifact_type,
        )
    )

    def case_06_reject_missing_required_field():
        bad = _decision_record()
        del bad["payload"]["approved"]
        build_refinement_promotion_record(bad)

    results.append(
        _expect_fail(
            "case_06_reject_missing_required_field",
            case_06_reject_missing_required_field,
        )
    )

    def case_07_reject_internal_field_leakage():
        bad = _decision_record()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_promotion_record(bad)

    results.append(
        _expect_fail(
            "case_07_reject_internal_field_leakage",
            case_07_reject_internal_field_leakage,
        )
    )

    def case_08_reject_invalid_decision_value():
        bad = _decision_record(
            approved=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "promoted",
                    "decision_reason": "bad_decision",
                }
            ],
            deferred=[],
            rejected=[],
        )
        build_refinement_promotion_record(bad)

    results.append(
        _expect_fail(
            "case_08_reject_invalid_decision_value",
            case_08_reject_invalid_decision_value,
        )
    )

    def case_09_reject_section_decision_mismatch():
        bad = _decision_record(
            approved=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "deferred",
                    "decision_reason": "score_3",
                }
            ],
            deferred=[],
            rejected=[],
        )
        build_refinement_promotion_record(bad)

    results.append(
        _expect_fail(
            "case_09_reject_section_decision_mismatch",
            case_09_reject_section_decision_mismatch,
        )
    )

    def case_10_zero_approved_supported():
        out = build_refinement_promotion_record(
            _decision_record(approved=[], deferred=[], rejected=[])
        )
        assert out["payload"]["promoted_count"] == 0
        assert out["payload"]["overflow_not_promoted_count"] == 0
        assert "no_items_promoted" in out["payload"]["promotion_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_approved_supported",
            case_10_zero_approved_supported,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage64_refinement_promotion_probe())
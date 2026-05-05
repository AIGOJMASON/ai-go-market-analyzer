from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_intake import (
    RefinementIntakeError,
    build_refinement_candidate_set,
)


def _analytics_summary(
    total_items_in_scope: int = 2,
    counts_by_closeout_state: dict | None = None,
    counts_by_intake_decision: dict | None = None,
    counts_by_target_child_core: dict | None = None,
    pattern_notes: list[str] | None = None,
    sealed: bool = True,
):
    return {
        "artifact_type": "analytics_summary",
        "payload": {
            "issuing_authority": "RUNTIME_ANALYTICS_SUMMARY",
            "total_items_in_scope": total_items_in_scope,
            "counts_by_closeout_state": counts_by_closeout_state
            if counts_by_closeout_state is not None
            else {"closed_accepted": 2},
            "counts_by_intake_decision": counts_by_intake_decision
            if counts_by_intake_decision is not None
            else {"accepted": 2},
            "counts_by_target_child_core": counts_by_target_child_core
            if counts_by_target_child_core is not None
            else {"proposal_saas": 2},
            "pattern_notes": pattern_notes
            if pattern_notes is not None
            else ["accepted_intake_majority", "single_child_core_scope:proposal_saas"],
            "sealed": sealed,
        },
    }


def _closeout(
    case_id: str,
    closeout_state: str = "closed_accepted",
    intake_decision: str = "accepted",
    target_child_core: str = "proposal_saas",
):
    return {
        "artifact_type": "case_closeout_record",
        "payload": {
            "case_id": case_id,
            "closeout_state": closeout_state,
            "final_state": "success",
            "target_child_core": target_child_core,
            "intake_decision": intake_decision,
            "created_at": "2026-03-20T00:00:00Z",
            "sealed": True,
        },
    }


def _review(
    case_id: str,
    intake_decision: str = "accepted",
    target_child_core: str = "proposal_saas",
):
    return {
        "artifact_type": "operator_review_view",
        "payload": {
            "case_id": case_id,
            "closeout_state": "closed_accepted",
            "final_state": "success",
            "target_child_core": target_child_core,
            "intake_decision": intake_decision,
            "created_at": "2026-03-20T00:00:00Z",
            "review_generated_at": "2026-03-20T00:05:00Z",
            "sealed": True,
        },
    }


def _retrieval(results, sealed: bool = True):
    return {
        "artifact_type": "archive_retrieval_result",
        "payload": {
            "issuing_authority": "RUNTIME_ARCHIVE_RETRIEVAL",
            "total_count": len(results),
            "filtered_count": len(results),
            "returned_count": len(results),
            "results": results,
            "filters": {},
            "limit": None,
            "offset": 0,
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
    except RefinementIntakeError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage61_refinement_intake_probe():
    results = []

    def case_01_valid_candidate_set_from_summary_only():
        out = build_refinement_candidate_set(
            _analytics_summary(
                total_items_in_scope=3,
                counts_by_closeout_state={"closed_accepted": 2, "closed_rejected": 1},
                counts_by_intake_decision={"accepted": 2, "rejected": 1},
                counts_by_target_child_core={"proposal_saas": 3},
                pattern_notes=["accepted_intake_majority", "single_child_core_scope:proposal_saas"],
            )
        )
        assert out["artifact_type"] == "refinement_candidate_set"
        assert out["payload"]["selected_count"] >= 1
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_candidate_set_from_summary_only",
            case_01_valid_candidate_set_from_summary_only,
        )
    )

    def case_02_valid_candidate_set_with_retrieval_context():
        out = build_refinement_candidate_set(
            _analytics_summary(
                total_items_in_scope=2,
                counts_by_closeout_state={"closed_accepted": 2},
                counts_by_intake_decision={"accepted": 2},
                counts_by_target_child_core={"gis": 2},
                pattern_notes=["accepted_intake_majority", "single_child_core_scope:gis"],
            ),
            _retrieval(
                [
                    _closeout("WR-6102-A", target_child_core="gis"),
                    _review("WR-6102-B", target_child_core="gis"),
                ]
            ),
        )
        assert out["artifact_type"] == "refinement_candidate_set"
        assert out["payload"]["retrieval_context_included"] is True

    results.append(
        _expect_pass(
            "case_02_valid_candidate_set_with_retrieval_context",
            case_02_valid_candidate_set_with_retrieval_context,
        )
    )

    def case_03_pattern_note_selection_present():
        out = build_refinement_candidate_set(
            _analytics_summary(
                pattern_notes=["accepted_intake_majority", "single_child_core_scope:proposal_saas"]
            )
        )
        selected = out["payload"]["selected_candidates"]
        values = [item["candidate_value"] for item in selected]
        assert "accepted_intake_majority" in values
        assert "single_child_core_scope:proposal_saas" in values

    results.append(
        _expect_pass(
            "case_03_pattern_note_selection_present",
            case_03_pattern_note_selection_present,
        )
    )

    def case_04_reject_unsealed_analytics_summary():
        build_refinement_candidate_set(_analytics_summary(sealed=False))

    results.append(
        _expect_fail(
            "case_04_reject_unsealed_analytics_summary",
            case_04_reject_unsealed_analytics_summary,
        )
    )

    def case_05_reject_invalid_summary_artifact_type():
        bad = _analytics_summary()
        bad["artifact_type"] = "operator_review_index"
        build_refinement_candidate_set(bad)

    results.append(
        _expect_fail(
            "case_05_reject_invalid_summary_artifact_type",
            case_05_reject_invalid_summary_artifact_type,
        )
    )

    def case_06_reject_missing_required_summary_fields():
        bad = _analytics_summary()
        del bad["payload"]["counts_by_closeout_state"]
        build_refinement_candidate_set(bad)

    results.append(
        _expect_fail(
            "case_06_reject_missing_required_summary_fields",
            case_06_reject_missing_required_summary_fields,
        )
    )

    def case_07_reject_internal_field_leakage_in_summary():
        bad = _analytics_summary()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_candidate_set(bad)

    results.append(
        _expect_fail(
            "case_07_reject_internal_field_leakage_in_summary",
            case_07_reject_internal_field_leakage_in_summary,
        )
    )

    def case_08_reject_unsealed_retrieval_context():
        build_refinement_candidate_set(
            _analytics_summary(),
            _retrieval([_closeout("WR-6108-A")], sealed=False),
        )

    results.append(
        _expect_fail(
            "case_08_reject_unsealed_retrieval_context",
            case_08_reject_unsealed_retrieval_context,
        )
    )

    def case_09_reject_invalid_retrieval_item_type():
        build_refinement_candidate_set(
            _analytics_summary(),
            _retrieval(
                [
                    {"artifact_type": "case_resolution", "payload": {"sealed": True}}
                ]
            ),
        )

    results.append(
        _expect_fail(
            "case_09_reject_invalid_retrieval_item_type",
            case_09_reject_invalid_retrieval_item_type,
        )
    )

    def case_10_zero_signal_supported_with_empty_selection():
        out = build_refinement_candidate_set(
            _analytics_summary(
                total_items_in_scope=0,
                counts_by_closeout_state={},
                counts_by_intake_decision={},
                counts_by_target_child_core={},
                pattern_notes=[],
            )
        )
        assert out["artifact_type"] == "refinement_candidate_set"
        assert out["payload"]["selected_count"] == 0
        assert out["payload"]["rejected_count"] >= 0
        assert "no_candidates_selected" in out["payload"]["selection_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_signal_supported_with_empty_selection",
            case_10_zero_signal_supported_with_empty_selection,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage61_refinement_intake_probe())
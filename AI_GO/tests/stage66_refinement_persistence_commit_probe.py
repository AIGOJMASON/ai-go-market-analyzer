from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_persistence_commit import (
    RefinementPersistenceCommitError,
    build_refinement_persistence_commit_record,
)


def _route_record(
    routed_items=None,
    visible_overflow_not_routed=None,
    visible_deferred_not_routed=None,
    visible_rejected_not_routed=None,
    sealed=True,
):
    return {
        "artifact_type": "refinement_persistence_route_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PERSISTENCE_ROUTING",
            "source_artifact_type": "refinement_promotion_record",
            "routed_count": len(routed_items) if routed_items is not None else 2,
            "visible_overflow_count": len(visible_overflow_not_routed) if visible_overflow_not_routed is not None else 1,
            "visible_deferred_count": len(visible_deferred_not_routed) if visible_deferred_not_routed is not None else 1,
            "visible_rejected_count": len(visible_rejected_not_routed) if visible_rejected_not_routed is not None else 1,
            "routed_items": routed_items
            if routed_items is not None
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
                    "promotion_status": "promoted",
                    "promotion_reason": "approved_for_controlled_persistence",
                    "route_status": "routed",
                    "route_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                        "refinement_governance_memory",
                    ],
                    "routing_reason": "promoted_for_durable_distribution",
                    "lineage_source_artifact_type": "refinement_promotion_record",
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
                    "promotion_status": "promoted",
                    "promotion_reason": "approved_for_controlled_persistence",
                    "route_status": "routed",
                    "route_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                    ],
                    "routing_reason": "promoted_for_durable_distribution",
                    "lineage_source_artifact_type": "refinement_promotion_record",
                },
            ],
            "visible_overflow_not_routed": visible_overflow_not_routed
            if visible_overflow_not_routed is not None
            else [
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "overflow_pattern",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 4,
                    "decision": "approved",
                    "decision_reason": "score_4",
                    "promotion_status": "not_promoted_cap_exceeded",
                    "promotion_reason": "promotion_cap_exceeded",
                    "lineage_source_artifact_type": "refinement_decision_record",
                }
            ],
            "visible_deferred_not_routed": visible_deferred_not_routed
            if visible_deferred_not_routed is not None
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
                    "promotion_status": "not_promoted_cap_exceeded",
                    "promotion_reason": "not_eligible_for_promotion",
                    "lineage_source_artifact_type": "refinement_decision_record",
                }
            ],
            "visible_rejected_not_routed": visible_rejected_not_routed
            if visible_rejected_not_routed is not None
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
                    "promotion_status": "not_promoted_cap_exceeded",
                    "promotion_reason": "not_eligible_for_promotion",
                    "lineage_source_artifact_type": "refinement_decision_record",
                }
            ],
            "routing_notes": [],
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
    except RefinementPersistenceCommitError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage66_refinement_persistence_commit_probe():
    results = []

    def case_01_valid_commit_record():
        out = build_refinement_persistence_commit_record(_route_record())
        assert out["artifact_type"] == "refinement_persistence_commit_record"
        assert out["payload"]["committed_count"] == 2
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_commit_record",
            case_01_valid_commit_record,
        )
    )

    def case_02_commit_targets_match_route_targets():
        out = build_refinement_persistence_commit_record(_route_record())
        for item in out["payload"]["committed_items"]:
            assert item["commit_targets"] == item["route_targets"]
            assert item["commit_status"] == "committed"

    results.append(
        _expect_pass(
            "case_02_commit_targets_match_route_targets",
            case_02_commit_targets_match_route_targets,
        )
    )

    def case_03_high_score_item_preserves_governance_memory_target():
        out = build_refinement_persistence_commit_record(_route_record())
        first = out["payload"]["committed_items"][0]
        assert "refinement_governance_memory" in first["commit_targets"]

    results.append(
        _expect_pass(
            "case_03_high_score_item_preserves_governance_memory_target",
            case_03_high_score_item_preserves_governance_memory_target,
        )
    )

    def case_04_reject_unsealed_input():
        build_refinement_persistence_commit_record(_route_record(sealed=False))

    results.append(
        _expect_fail(
            "case_04_reject_unsealed_input",
            case_04_reject_unsealed_input,
        )
    )

    def case_05_reject_invalid_artifact_type():
        bad = _route_record()
        bad["artifact_type"] = "refinement_promotion_record"
        build_refinement_persistence_commit_record(bad)

    results.append(
        _expect_fail(
            "case_05_reject_invalid_artifact_type",
            case_05_reject_invalid_artifact_type,
        )
    )

    def case_06_reject_missing_required_field():
        bad = _route_record()
        del bad["payload"]["routed_items"]
        build_refinement_persistence_commit_record(bad)

    results.append(
        _expect_fail(
            "case_06_reject_missing_required_field",
            case_06_reject_missing_required_field,
        )
    )

    def case_07_reject_internal_field_leakage():
        bad = _route_record()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_persistence_commit_record(bad)

    results.append(
        _expect_fail(
            "case_07_reject_internal_field_leakage",
            case_07_reject_internal_field_leakage,
        )
    )

    def case_08_reject_invalid_route_status():
        bad = _route_record(
            routed_items=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "approved",
                    "decision_reason": "score_5",
                    "promotion_status": "promoted",
                    "promotion_reason": "approved_for_controlled_persistence",
                    "route_status": "queued",
                    "route_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                    ],
                    "routing_reason": "bad_status",
                    "lineage_source_artifact_type": "refinement_promotion_record",
                }
            ],
            visible_overflow_not_routed=[],
            visible_deferred_not_routed=[],
            visible_rejected_not_routed=[],
        )
        build_refinement_persistence_commit_record(bad)

    results.append(
        _expect_fail(
            "case_08_reject_invalid_route_status",
            case_08_reject_invalid_route_status,
        )
    )

    def case_09_reject_invalid_route_target():
        bad = _route_record(
            routed_items=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "approved",
                    "decision_reason": "score_5",
                    "promotion_status": "promoted",
                    "promotion_reason": "approved_for_controlled_persistence",
                    "route_status": "routed",
                    "route_targets": [
                        "refinement_archive",
                        "illegal_target",
                    ],
                    "routing_reason": "bad_target",
                    "lineage_source_artifact_type": "refinement_promotion_record",
                }
            ],
            visible_overflow_not_routed=[],
            visible_deferred_not_routed=[],
            visible_rejected_not_routed=[],
        )
        build_refinement_persistence_commit_record(bad)

    results.append(
        _expect_fail(
            "case_09_reject_invalid_route_target",
            case_09_reject_invalid_route_target,
        )
    )

    def case_10_zero_routed_supported():
        out = build_refinement_persistence_commit_record(
            _route_record(
                routed_items=[],
                visible_overflow_not_routed=[],
                visible_deferred_not_routed=[],
                visible_rejected_not_routed=[],
            )
        )
        assert out["payload"]["committed_count"] == 0
        assert "no_items_committed" in out["payload"]["commit_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_routed_supported",
            case_10_zero_routed_supported,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage66_refinement_persistence_commit_probe())
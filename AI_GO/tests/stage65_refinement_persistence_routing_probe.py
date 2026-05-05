from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_persistence_routing import (
    RefinementPersistenceRoutingError,
    build_refinement_persistence_route_record,
)


def _promotion_record(
    promoted=None,
    overflow_not_promoted=None,
    deferred_visible=None,
    rejected_visible=None,
    sealed=True,
):
    return {
        "artifact_type": "refinement_promotion_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PROMOTION",
            "source_artifact_type": "refinement_decision_record",
            "promoted_count": len(promoted) if promoted is not None else 2,
            "overflow_not_promoted_count": len(overflow_not_promoted) if overflow_not_promoted is not None else 1,
            "deferred_visible_count": len(deferred_visible) if deferred_visible is not None else 1,
            "rejected_visible_count": len(rejected_visible) if rejected_visible is not None else 1,
            "promoted": promoted
            if promoted is not None
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
                    "lineage_source_artifact_type": "refinement_decision_record",
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
                    "lineage_source_artifact_type": "refinement_decision_record",
                },
            ],
            "overflow_not_promoted": overflow_not_promoted
            if overflow_not_promoted is not None
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
            "deferred_visible": deferred_visible
            if deferred_visible is not None
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
            "rejected_visible": rejected_visible
            if rejected_visible is not None
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
            "promotion_notes": [],
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
    except RefinementPersistenceRoutingError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage65_refinement_persistence_routing_probe():
    results = []

    def case_01_valid_route_record():
        out = build_refinement_persistence_route_record(_promotion_record())
        assert out["artifact_type"] == "refinement_persistence_route_record"
        assert out["payload"]["routed_count"] == 2
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_route_record",
            case_01_valid_route_record,
        )
    )

    def case_02_only_promoted_items_are_routed():
        out = build_refinement_persistence_route_record(_promotion_record())
        routed = out["payload"]["routed_items"]
        assert [item["promotion_status"] for item in routed] == ["promoted", "promoted"]
        assert [item["decision"] for item in routed] == ["approved", "approved"]

    results.append(
        _expect_pass(
            "case_02_only_promoted_items_are_routed",
            case_02_only_promoted_items_are_routed,
        )
    )

    def case_03_high_score_gets_governance_memory_route():
        out = build_refinement_persistence_route_record(_promotion_record())
        first = out["payload"]["routed_items"][0]
        assert "refinement_governance_memory" in first["route_targets"]

    results.append(
        _expect_pass(
            "case_03_high_score_gets_governance_memory_route",
            case_03_high_score_gets_governance_memory_route,
        )
    )

    def case_04_reject_unsealed_input():
        build_refinement_persistence_route_record(_promotion_record(sealed=False))

    results.append(
        _expect_fail(
            "case_04_reject_unsealed_input",
            case_04_reject_unsealed_input,
        )
    )

    def case_05_reject_invalid_artifact_type():
        bad = _promotion_record()
        bad["artifact_type"] = "refinement_decision_record"
        build_refinement_persistence_route_record(bad)

    results.append(
        _expect_fail(
            "case_05_reject_invalid_artifact_type",
            case_05_reject_invalid_artifact_type,
        )
    )

    def case_06_reject_missing_required_field():
        bad = _promotion_record()
        del bad["payload"]["promoted"]
        build_refinement_persistence_route_record(bad)

    results.append(
        _expect_fail(
            "case_06_reject_missing_required_field",
            case_06_reject_missing_required_field,
        )
    )

    def case_07_reject_internal_field_leakage():
        bad = _promotion_record()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_persistence_route_record(bad)

    results.append(
        _expect_fail(
            "case_07_reject_internal_field_leakage",
            case_07_reject_internal_field_leakage,
        )
    )

    def case_08_reject_invalid_promotion_status_on_promoted_item():
        bad = _promotion_record(
            promoted=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "approved",
                    "decision_reason": "score_5",
                    "promotion_status": "queued",
                    "promotion_reason": "bad_status",
                    "lineage_source_artifact_type": "refinement_decision_record",
                }
            ],
            overflow_not_promoted=[],
            deferred_visible=[],
            rejected_visible=[],
        )
        build_refinement_persistence_route_record(bad)

    results.append(
        _expect_fail(
            "case_08_reject_invalid_promotion_status_on_promoted_item",
            case_08_reject_invalid_promotion_status_on_promoted_item,
        )
    )

    def case_09_reject_promoted_section_decision_mismatch():
        bad = _promotion_record(
            promoted=[
                {
                    "candidate_type": "pattern_note",
                    "candidate_source": "pattern_notes",
                    "candidate_value": "x",
                    "selection_reason": "approved_pattern_note",
                    "score_components": [],
                    "total_score": 5,
                    "decision": "deferred",
                    "decision_reason": "score_3",
                    "promotion_status": "promoted",
                    "promotion_reason": "approved_for_controlled_persistence",
                    "lineage_source_artifact_type": "refinement_decision_record",
                }
            ],
            overflow_not_promoted=[],
            deferred_visible=[],
            rejected_visible=[],
        )
        build_refinement_persistence_route_record(bad)

    results.append(
        _expect_fail(
            "case_09_reject_promoted_section_decision_mismatch",
            case_09_reject_promoted_section_decision_mismatch,
        )
    )

    def case_10_zero_promoted_supported():
        out = build_refinement_persistence_route_record(
            _promotion_record(
                promoted=[],
                overflow_not_promoted=[],
                deferred_visible=[],
                rejected_visible=[],
            )
        )
        assert out["payload"]["routed_count"] == 0
        assert "no_items_routed" in out["payload"]["routing_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_promoted_supported",
            case_10_zero_promoted_supported,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage65_refinement_persistence_routing_probe())
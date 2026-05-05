from __future__ import annotations

from AI_GO.core.runtime.refinement.refinement_consumer_interface import (
    RefinementConsumerInterfaceError,
    build_refinement_consumer_packet,
)


def _commit_record(
    committed_items=None,
    sealed=True,
):
    return {
        "artifact_type": "refinement_persistence_commit_record",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_PERSISTENCE_COMMIT",
            "source_artifact_type": "refinement_persistence_route_record",
            "committed_count": len(committed_items) if committed_items is not None else 2,
            "visible_overflow_count": 1,
            "visible_deferred_count": 1,
            "visible_rejected_count": 1,
            "committed_items": committed_items
            if committed_items is not None
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
                    "commit_status": "committed",
                    "commit_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                        "refinement_governance_memory",
                    ],
                    "commit_reason": "routed_for_durable_commit",
                    "lineage_source_artifact_type": "refinement_persistence_route_record",
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
                    "commit_status": "committed",
                    "commit_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                    ],
                    "commit_reason": "routed_for_durable_commit",
                    "lineage_source_artifact_type": "refinement_persistence_route_record",
                },
            ],
            "visible_overflow_not_committed": [],
            "visible_deferred_not_committed": [],
            "visible_rejected_not_committed": [],
            "commit_notes": [],
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
    except RefinementConsumerInterfaceError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage67_refinement_consumer_interface_probe():
    results = []

    def case_01_valid_consumer_packet():
        out = build_refinement_consumer_packet(_commit_record())
        assert out["artifact_type"] == "refinement_consumer_packet"
        assert out["payload"]["sealed"] is True

    results.append(
        _expect_pass(
            "case_01_valid_consumer_packet",
            case_01_valid_consumer_packet,
        )
    )

    def case_02_rosetta_and_curved_mirror_packets_present():
        out = build_refinement_consumer_packet(_commit_record())
        assert out["payload"]["rosetta_packet_count"] == 2
        assert out["payload"]["curved_mirror_packet_count"] == 2

    results.append(
        _expect_pass(
            "case_02_rosetta_and_curved_mirror_packets_present",
            case_02_rosetta_and_curved_mirror_packets_present,
        )
    )

    def case_03_rosetta_packet_is_human_facing_shape():
        out = build_refinement_consumer_packet(_commit_record())
        first = out["payload"]["rosetta_packet"][0]
        assert "guidance_type" in first
        assert "guidance_text" in first
        assert "total_score" in first

    results.append(
        _expect_pass(
            "case_03_rosetta_packet_is_human_facing_shape",
            case_03_rosetta_packet_is_human_facing_shape,
        )
    )

    def case_04_curved_mirror_packet_is_structural_shape():
        out = build_refinement_consumer_packet(_commit_record())
        first = out["payload"]["curved_mirror_packet"][0]
        assert "signal_type" in first
        assert "signal_value" in first
        assert "commit_targets" in first

    results.append(
        _expect_pass(
            "case_04_curved_mirror_packet_is_structural_shape",
            case_04_curved_mirror_packet_is_structural_shape,
        )
    )

    def case_05_reject_unsealed_input():
        build_refinement_consumer_packet(_commit_record(sealed=False))

    results.append(
        _expect_fail(
            "case_05_reject_unsealed_input",
            case_05_reject_unsealed_input,
        )
    )

    def case_06_reject_invalid_artifact_type():
        bad = _commit_record()
        bad["artifact_type"] = "refinement_persistence_route_record"
        build_refinement_consumer_packet(bad)

    results.append(
        _expect_fail(
            "case_06_reject_invalid_artifact_type",
            case_06_reject_invalid_artifact_type,
        )
    )

    def case_07_reject_missing_required_field():
        bad = _commit_record()
        del bad["payload"]["committed_items"]
        build_refinement_consumer_packet(bad)

    results.append(
        _expect_fail(
            "case_07_reject_missing_required_field",
            case_07_reject_missing_required_field,
        )
    )

    def case_08_reject_internal_field_leakage():
        bad = _commit_record()
        bad["payload"]["_internal"] = {"unsafe": True}
        build_refinement_consumer_packet(bad)

    results.append(
        _expect_fail(
            "case_08_reject_internal_field_leakage",
            case_08_reject_internal_field_leakage,
        )
    )

    def case_09_reject_invalid_commit_status():
        bad = _commit_record(
            committed_items=[
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
                        "refinement_review_surface",
                    ],
                    "routing_reason": "promoted_for_durable_distribution",
                    "commit_status": "pending",
                    "commit_targets": [
                        "refinement_archive",
                        "refinement_review_surface",
                    ],
                    "commit_reason": "bad_commit_status",
                    "lineage_source_artifact_type": "refinement_persistence_route_record",
                }
            ]
        )
        build_refinement_consumer_packet(bad)

    results.append(
        _expect_fail(
            "case_09_reject_invalid_commit_status",
            case_09_reject_invalid_commit_status,
        )
    )

    def case_10_zero_committed_supported():
        out = build_refinement_consumer_packet(_commit_record(committed_items=[]))
        assert out["payload"]["committed_input_count"] == 0
        assert "no_consumer_items_available" in out["payload"]["consumer_notes"]

    results.append(
        _expect_pass(
            "case_10_zero_committed_supported",
            case_10_zero_committed_supported,
        )
    )

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage67_refinement_consumer_interface_probe())
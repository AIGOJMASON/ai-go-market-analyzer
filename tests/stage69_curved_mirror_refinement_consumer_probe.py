from __future__ import annotations

from AI_GO.core.runtime.refinement.curved_mirror_refinement_consumer import (
    CurvedMirrorRefinementConsumerError,
    build_curved_mirror_refinement_receipt,
)


def _consumer_packet(curved_mirror_packet=None, sealed=True):
    return {
        "artifact_type": "refinement_consumer_packet",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_CONSUMER_INTERFACE",
            "source_artifact_type": "refinement_persistence_commit_record",
            "committed_input_count": 2,
            "rosetta_packet_count": 2,
            "curved_mirror_packet_count": len(curved_mirror_packet) if curved_mirror_packet is not None else 2,
            "rosetta_packet": [],
            "curved_mirror_packet": curved_mirror_packet
            if curved_mirror_packet is not None
            else [
                {
                    "signal_type": "pattern_note",
                    "signal_value": "accepted_intake_majority",
                    "total_score": 5,
                    "commit_targets": ["refinement_archive"],
                    "source_candidate_type": "pattern_note",
                },
                {
                    "signal_type": "target_child_core_count",
                    "signal_value": {"proposal_saas": 4},
                    "total_score": 4,
                    "commit_targets": ["refinement_archive"],
                    "source_candidate_type": "target_child_core_count",
                },
            ],
            "consumer_notes": [],
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
    except CurvedMirrorRefinementConsumerError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage69_curved_mirror_refinement_consumer_probe():
    results = []

    def case_01_valid_receipt():
        out = build_curved_mirror_refinement_receipt(_consumer_packet())
        assert out["artifact_type"] == "curved_mirror_refinement_receipt"
        assert out["payload"]["sealed"] is True

    results.append(_expect_pass("case_01_valid_receipt", case_01_valid_receipt))

    def case_02_consumed_count_matches():
        out = build_curved_mirror_refinement_receipt(_consumer_packet())
        assert out["payload"]["consumed_count"] == 2

    results.append(_expect_pass("case_02_consumed_count_matches", case_02_consumed_count_matches))

    def case_03_signal_structure_valid():
        out = build_curved_mirror_refinement_receipt(_consumer_packet())
        first = out["payload"]["curved_mirror_signals"][0]
        assert "signal_type" in first
        assert "signal_value" in first

    results.append(_expect_pass("case_03_signal_structure_valid", case_03_signal_structure_valid))

    def case_04_reject_unsealed():
        build_curved_mirror_refinement_receipt(_consumer_packet(sealed=False))

    results.append(_expect_fail("case_04_reject_unsealed", case_04_reject_unsealed))

    def case_05_reject_invalid_artifact_type():
        bad = _consumer_packet()
        bad["artifact_type"] = "wrong"
        build_curved_mirror_refinement_receipt(bad)

    results.append(_expect_fail("case_05_reject_invalid_artifact_type", case_05_reject_invalid_artifact_type))

    def case_06_reject_missing_curved_mirror_packet():
        bad = _consumer_packet()
        del bad["payload"]["curved_mirror_packet"]
        build_curved_mirror_refinement_receipt(bad)

    results.append(_expect_fail("case_06_reject_missing_curved_mirror_packet", case_06_reject_missing_curved_mirror_packet))

    def case_07_reject_invalid_entry_structure():
        bad = _consumer_packet(curved_mirror_packet=[{"bad": "data"}])
        build_curved_mirror_refinement_receipt(bad)

    results.append(_expect_fail("case_07_reject_invalid_entry_structure", case_07_reject_invalid_entry_structure))

    def case_08_reject_internal_field_leakage():
        bad = _consumer_packet()
        bad["payload"]["_internal"] = True
        build_curved_mirror_refinement_receipt(bad)

    results.append(_expect_fail("case_08_reject_internal_field_leakage", case_08_reject_internal_field_leakage))

    def case_09_zero_entries_supported():
        out = build_curved_mirror_refinement_receipt(
            _consumer_packet(curved_mirror_packet=[])
        )
        assert out["payload"]["consumed_count"] == 0

    results.append(_expect_pass("case_09_zero_entries_supported", case_09_zero_entries_supported))

    def case_10_notes_present_on_empty():
        out = build_curved_mirror_refinement_receipt(
            _consumer_packet(curved_mirror_packet=[])
        )
        assert "no_curved_mirror_signals_available" in out["payload"]["consumer_notes"]

    results.append(_expect_pass("case_10_notes_present_on_empty", case_10_notes_present_on_empty))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage69_curved_mirror_refinement_consumer_probe())
from __future__ import annotations

from AI_GO.core.runtime.refinement.rosetta_refinement_consumer import (
    RosettaRefinementConsumerError,
    build_rosetta_refinement_receipt,
)


def _consumer_packet(rosetta_packet=None, sealed=True):
    return {
        "artifact_type": "refinement_consumer_packet",
        "payload": {
            "issuing_authority": "RUNTIME_REFINEMENT_CONSUMER_INTERFACE",
            "source_artifact_type": "refinement_persistence_commit_record",
            "committed_input_count": 2,
            "rosetta_packet_count": len(rosetta_packet) if rosetta_packet is not None else 2,
            "curved_mirror_packet_count": 2,
            "rosetta_packet": rosetta_packet
            if rosetta_packet is not None
            else [
                {
                    "guidance_type": "pattern_note",
                    "guidance_text": "Committed refinement signal",
                    "source_candidate_type": "pattern_note",
                    "total_score": 5,
                    "commit_targets": ["refinement_archive"],
                },
                {
                    "guidance_type": "target_child_core_count",
                    "guidance_text": "Count signal",
                    "source_candidate_type": "target_child_core_count",
                    "total_score": 4,
                    "commit_targets": ["refinement_archive"],
                },
            ],
            "curved_mirror_packet": [],
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
    except RosettaRefinementConsumerError:
        return {"case": name, "status": "passed"}
    except Exception as exc:
        return {"case": name, "status": "failed", "error": str(exc)}


def run_stage68_rosetta_refinement_consumer_probe():
    results = []

    def case_01_valid_receipt():
        out = build_rosetta_refinement_receipt(_consumer_packet())
        assert out["artifact_type"] == "rosetta_refinement_receipt"
        assert out["payload"]["sealed"] is True

    results.append(_expect_pass("case_01_valid_receipt", case_01_valid_receipt))

    def case_02_consumed_count_matches():
        out = build_rosetta_refinement_receipt(_consumer_packet())
        assert out["payload"]["consumed_count"] == 2

    results.append(_expect_pass("case_02_consumed_count_matches", case_02_consumed_count_matches))

    def case_03_guidance_structure_valid():
        out = build_rosetta_refinement_receipt(_consumer_packet())
        first = out["payload"]["rosetta_guidance"][0]
        assert "guidance_type" in first
        assert "guidance_text" in first

    results.append(_expect_pass("case_03_guidance_structure_valid", case_03_guidance_structure_valid))

    def case_04_reject_unsealed():
        build_rosetta_refinement_receipt(_consumer_packet(sealed=False))

    results.append(_expect_fail("case_04_reject_unsealed", case_04_reject_unsealed))

    def case_05_reject_invalid_artifact_type():
        bad = _consumer_packet()
        bad["artifact_type"] = "wrong"
        build_rosetta_refinement_receipt(bad)

    results.append(_expect_fail("case_05_reject_invalid_artifact_type", case_05_reject_invalid_artifact_type))

    def case_06_reject_missing_rosetta_packet():
        bad = _consumer_packet()
        del bad["payload"]["rosetta_packet"]
        build_rosetta_refinement_receipt(bad)

    results.append(_expect_fail("case_06_reject_missing_rosetta_packet", case_06_reject_missing_rosetta_packet))

    def case_07_reject_invalid_entry_structure():
        bad = _consumer_packet(rosetta_packet=[{"bad": "data"}])
        build_rosetta_refinement_receipt(bad)

    results.append(_expect_fail("case_07_reject_invalid_entry_structure", case_07_reject_invalid_entry_structure))

    def case_08_reject_internal_field_leakage():
        bad = _consumer_packet()
        bad["payload"]["_internal"] = True
        build_rosetta_refinement_receipt(bad)

    results.append(_expect_fail("case_08_reject_internal_field_leakage", case_08_reject_internal_field_leakage))

    def case_09_zero_entries_supported():
        out = build_rosetta_refinement_receipt(_consumer_packet(rosetta_packet=[]))
        assert out["payload"]["consumed_count"] == 0

    results.append(_expect_pass("case_09_zero_entries_supported", case_09_zero_entries_supported))

    def case_10_notes_present_on_empty():
        out = build_rosetta_refinement_receipt(_consumer_packet(rosetta_packet=[]))
        assert "no_rosetta_guidance_available" in out["payload"]["consumer_notes"]

    results.append(_expect_pass("case_10_notes_present_on_empty", case_10_notes_present_on_empty))

    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_stage68_rosetta_refinement_consumer_probe())
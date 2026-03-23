from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_execution_intake import (
    build_child_core_execution_packet_from_fusion,
)


def _valid_fusion_record() -> dict:
    return {
        "artifact_type": "execution_fusion_record",
        "sealed": True,
        "case_id": "CASE-74-001",
        "source_rosetta_artifact_type": "rosetta_runtime_execution_state",
        "source_curved_mirror_artifact_type": "curved_mirror_runtime_execution_state",
        "weights": {
            "rosetta_weight": 0.20,
            "curved_mirror_weight": 0.80,
        },
        "runtime_modes": {
            "rosetta_mode": "rosetta_refined_runtime",
            "curved_mirror_mode": "curved_mirror_refined_runtime",
        },
        "downstream_status": "ready_for_child_core",
        "child_core_handoff": "fused_execution_ready",
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_child_core_execution_packet():
    result = build_child_core_execution_packet_from_fusion(
        _valid_fusion_record(),
        "proposal_builder",
    )

    assert result["artifact_type"] == "child_core_execution_packet"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-74-001"
    assert result["child_core_target"] == "proposal_builder"
    assert result["weights"]["rosetta_weight"] == 0.20
    assert result["weights"]["curved_mirror_weight"] == 0.80
    assert result["runtime_modes"]["rosetta_mode"] == "rosetta_refined_runtime"
    assert result["runtime_modes"]["curved_mirror_mode"] == "curved_mirror_refined_runtime"
    assert result["intake_status"] == "ready_for_execution_surface"


def case_02_reject_invalid_fusion_artifact_type():
    record = _valid_fusion_record()
    record["artifact_type"] = "wrong_type"

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_fusion_record():
    record = _valid_fusion_record()
    record["sealed"] = False

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_invalid_child_core_target():
    try:
        build_child_core_execution_packet_from_fusion(_valid_fusion_record(), "unknown_core")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_invalid_rosetta_source_artifact_type():
    record = _valid_fusion_record()
    record["source_rosetta_artifact_type"] = "wrong_type"

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_invalid_handoff_posture():
    record = _valid_fusion_record()
    record["child_core_handoff"] = "wrong_handoff"

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_combined_weight_over_one():
    record = _valid_fusion_record()
    record["weights"]["rosetta_weight"] = 0.60
    record["weights"]["curved_mirror_weight"] = 0.60

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_invalid_runtime_mode():
    record = _valid_fusion_record()
    record["runtime_modes"]["curved_mirror_mode"] = "wrong_mode"

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_zero_entry_compatible_posture_supported():
    result = build_child_core_execution_packet_from_fusion(
        _valid_fusion_record(),
        "gis",
    )
    assert result["child_core_target"] == "gis"
    assert result["intake_status"] == "ready_for_execution_surface"


def case_10_reject_internal_field_leakage():
    record = _valid_fusion_record()
    record["_debug"] = {"illegal": True}

    try:
        build_child_core_execution_packet_from_fusion(record, "proposal_builder")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_child_core_execution_packet", case_01_valid_child_core_execution_packet),
        ("case_02_reject_invalid_fusion_artifact_type", case_02_reject_invalid_fusion_artifact_type),
        ("case_03_reject_unsealed_fusion_record", case_03_reject_unsealed_fusion_record),
        ("case_04_reject_invalid_child_core_target", case_04_reject_invalid_child_core_target),
        ("case_05_reject_invalid_rosetta_source_artifact_type", case_05_reject_invalid_rosetta_source_artifact_type),
        ("case_06_reject_invalid_handoff_posture", case_06_reject_invalid_handoff_posture),
        ("case_07_reject_combined_weight_over_one", case_07_reject_combined_weight_over_one),
        ("case_08_reject_invalid_runtime_mode", case_08_reject_invalid_runtime_mode),
        ("case_09_zero_entry_compatible_posture_supported", case_09_zero_entry_compatible_posture_supported),
        ("case_10_reject_internal_field_leakage", case_10_reject_internal_field_leakage),
    ]

    results = [_run_case(name, fn) for name, fn in cases]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()
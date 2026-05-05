from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_execution_surface import (
    build_child_core_execution_result_from_packet,
)


def _valid_execution_packet() -> dict:
    return {
        "artifact_type": "child_core_execution_packet",
        "sealed": True,
        "case_id": "CASE-75-001",
        "source_artifact_type": "execution_fusion_record",
        "child_core_target": "proposal_builder",
        "weights": {
            "rosetta_weight": 0.20,
            "curved_mirror_weight": 0.80,
        },
        "runtime_modes": {
            "rosetta_mode": "rosetta_refined_runtime",
            "curved_mirror_mode": "curved_mirror_refined_runtime",
        },
        "downstream_status": "ready_for_child_core",
        "intake_status": "ready_for_execution_surface",
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_child_core_execution_result():
    result = build_child_core_execution_result_from_packet(_valid_execution_packet())

    assert result["artifact_type"] == "child_core_execution_result"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-75-001"
    assert result["child_core_target"] == "proposal_builder"
    assert result["weights"]["rosetta_weight"] == 0.20
    assert result["weights"]["curved_mirror_weight"] == 0.80
    assert result["runtime_modes"]["rosetta_mode"] == "rosetta_refined_runtime"
    assert result["runtime_modes"]["curved_mirror_mode"] == "curved_mirror_refined_runtime"
    assert result["execution_status"] == "execution_surface_complete"
    assert result["downstream_status"] == "ready_for_result_handling"


def case_02_reject_invalid_packet_artifact_type():
    packet = _valid_execution_packet()
    packet["artifact_type"] = "wrong_type"

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_packet():
    packet = _valid_execution_packet()
    packet["sealed"] = False

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_invalid_child_core_target():
    packet = _valid_execution_packet()
    packet["child_core_target"] = "unknown_core"

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_invalid_source_artifact_type():
    packet = _valid_execution_packet()
    packet["source_artifact_type"] = "wrong_type"

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_invalid_intake_status():
    packet = _valid_execution_packet()
    packet["intake_status"] = "wrong_status"

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_combined_weight_over_one():
    packet = _valid_execution_packet()
    packet["weights"]["rosetta_weight"] = 0.60
    packet["weights"]["curved_mirror_weight"] = 0.60

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_invalid_runtime_mode():
    packet = _valid_execution_packet()
    packet["runtime_modes"]["rosetta_mode"] = "wrong_mode"

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_zero_entry_compatible_posture_supported():
    packet = _valid_execution_packet()
    packet["child_core_target"] = "gis"

    result = build_child_core_execution_result_from_packet(packet)
    assert result["child_core_target"] == "gis"
    assert result["execution_status"] == "execution_surface_complete"


def case_10_reject_internal_field_leakage():
    packet = _valid_execution_packet()
    packet["_debug"] = {"illegal": True}

    try:
        build_child_core_execution_result_from_packet(packet)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_child_core_execution_result", case_01_valid_child_core_execution_result),
        ("case_02_reject_invalid_packet_artifact_type", case_02_reject_invalid_packet_artifact_type),
        ("case_03_reject_unsealed_packet", case_03_reject_unsealed_packet),
        ("case_04_reject_invalid_child_core_target", case_04_reject_invalid_child_core_target),
        ("case_05_reject_invalid_source_artifact_type", case_05_reject_invalid_source_artifact_type),
        ("case_06_reject_invalid_intake_status", case_06_reject_invalid_intake_status),
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
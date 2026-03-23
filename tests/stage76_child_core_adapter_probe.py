from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_adapter import (
    build_child_core_adapter_packet_from_result,
)


def _valid_execution_result() -> dict:
    return {
        "artifact_type": "child_core_execution_result",
        "sealed": True,
        "case_id": "CASE-76-001",
        "source_artifact_type": "child_core_execution_packet",
        "child_core_target": "proposal_builder",
        "weights": {
            "rosetta_weight": 0.20,
            "curved_mirror_weight": 0.80,
        },
        "runtime_modes": {
            "rosetta_mode": "rosetta_refined_runtime",
            "curved_mirror_mode": "curved_mirror_refined_runtime",
        },
        "execution_status": "execution_surface_complete",
        "downstream_status": "ready_for_result_handling",
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_child_core_adapter_packet():
    result = build_child_core_adapter_packet_from_result(_valid_execution_result())

    assert result["artifact_type"] == "child_core_adapter_packet"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-76-001"
    assert result["child_core_target"] == "proposal_builder"
    assert result["adapter_class"] == "proposal_adapter"
    assert result["weights"]["rosetta_weight"] == 0.20
    assert result["weights"]["curved_mirror_weight"] == 0.80
    assert result["runtime_modes"]["rosetta_mode"] == "rosetta_refined_runtime"
    assert result["runtime_modes"]["curved_mirror_mode"] == "curved_mirror_refined_runtime"
    assert result["adapter_status"] == "ready_for_target_adapter"


def case_02_reject_invalid_result_artifact_type():
    payload = _valid_execution_result()
    payload["artifact_type"] = "wrong_type"

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_result():
    payload = _valid_execution_result()
    payload["sealed"] = False

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_invalid_child_core_target():
    payload = _valid_execution_result()
    payload["child_core_target"] = "unknown_core"

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_invalid_source_artifact_type():
    payload = _valid_execution_result()
    payload["source_artifact_type"] = "wrong_type"

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_invalid_execution_status():
    payload = _valid_execution_result()
    payload["execution_status"] = "wrong_status"

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_combined_weight_over_one():
    payload = _valid_execution_result()
    payload["weights"]["rosetta_weight"] = 0.70
    payload["weights"]["curved_mirror_weight"] = 0.70

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_invalid_runtime_mode():
    payload = _valid_execution_result()
    payload["runtime_modes"]["curved_mirror_mode"] = "wrong_mode"

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_other_target_maps_to_correct_adapter():
    payload = _valid_execution_result()
    payload["child_core_target"] = "gis"

    result = build_child_core_adapter_packet_from_result(payload)
    assert result["child_core_target"] == "gis"
    assert result["adapter_class"] == "gis_adapter"


def case_10_reject_internal_field_leakage():
    payload = _valid_execution_result()
    payload["_debug"] = {"illegal": True}

    try:
        build_child_core_adapter_packet_from_result(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_child_core_adapter_packet", case_01_valid_child_core_adapter_packet),
        ("case_02_reject_invalid_result_artifact_type", case_02_reject_invalid_result_artifact_type),
        ("case_03_reject_unsealed_result", case_03_reject_unsealed_result),
        ("case_04_reject_invalid_child_core_target", case_04_reject_invalid_child_core_target),
        ("case_05_reject_invalid_source_artifact_type", case_05_reject_invalid_source_artifact_type),
        ("case_06_reject_invalid_execution_status", case_06_reject_invalid_execution_status),
        ("case_07_reject_combined_weight_over_one", case_07_reject_combined_weight_over_one),
        ("case_08_reject_invalid_runtime_mode", case_08_reject_invalid_runtime_mode),
        ("case_09_other_target_maps_to_correct_adapter", case_09_other_target_maps_to_correct_adapter),
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
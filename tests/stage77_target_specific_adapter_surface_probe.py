from __future__ import annotations

from AI_GO.core.runtime.refinement.target_specific_adapter_surface import (
    build_target_specific_adapter_packet_from_adapter,
)


def _valid_adapter_packet() -> dict:
    return {
        "artifact_type": "child_core_adapter_packet",
        "sealed": True,
        "case_id": "CASE-77-001",
        "source_artifact_type": "child_core_execution_result",
        "child_core_target": "proposal_builder",
        "adapter_class": "proposal_adapter",
        "weights": {
            "rosetta_weight": 0.20,
            "curved_mirror_weight": 0.80,
        },
        "runtime_modes": {
            "rosetta_mode": "rosetta_refined_runtime",
            "curved_mirror_mode": "curved_mirror_refined_runtime",
        },
        "adapter_status": "ready_for_target_adapter",
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


def case_01_valid_target_specific_adapter_packet():
    result = build_target_specific_adapter_packet_from_adapter(_valid_adapter_packet())

    assert result["artifact_type"] == "target_specific_adapter_packet"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-77-001"
    assert result["child_core_target"] == "proposal_builder"
    assert result["adapter_class"] == "proposal_adapter"
    assert result["target_surface_class"] == "proposal_target_surface"
    assert result["adapter_status"] == "ready_for_target_implementation"


def case_02_reject_invalid_adapter_packet_artifact_type():
    payload = _valid_adapter_packet()
    payload["artifact_type"] = "wrong_type"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_adapter_packet():
    payload = _valid_adapter_packet()
    payload["sealed"] = False

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_invalid_child_core_target():
    payload = _valid_adapter_packet()
    payload["child_core_target"] = "unknown_core"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_mismatched_adapter_class():
    payload = _valid_adapter_packet()
    payload["adapter_class"] = "gis_adapter"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_invalid_source_artifact_type():
    payload = _valid_adapter_packet()
    payload["source_artifact_type"] = "wrong_type"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_invalid_adapter_status():
    payload = _valid_adapter_packet()
    payload["adapter_status"] = "wrong_status"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_invalid_runtime_mode():
    payload = _valid_adapter_packet()
    payload["runtime_modes"]["curved_mirror_mode"] = "wrong_mode"

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_other_target_maps_to_correct_surface():
    payload = _valid_adapter_packet()
    payload["child_core_target"] = "gis"
    payload["adapter_class"] = "gis_adapter"

    result = build_target_specific_adapter_packet_from_adapter(payload)
    assert result["child_core_target"] == "gis"
    assert result["adapter_class"] == "gis_adapter"
    assert result["target_surface_class"] == "gis_target_surface"


def case_10_reject_internal_field_leakage():
    payload = _valid_adapter_packet()
    payload["_debug"] = {"illegal": True}

    try:
        build_target_specific_adapter_packet_from_adapter(payload)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_target_specific_adapter_packet", case_01_valid_target_specific_adapter_packet),
        ("case_02_reject_invalid_adapter_packet_artifact_type", case_02_reject_invalid_adapter_packet_artifact_type),
        ("case_03_reject_unsealed_adapter_packet", case_03_reject_unsealed_adapter_packet),
        ("case_04_reject_invalid_child_core_target", case_04_reject_invalid_child_core_target),
        ("case_05_reject_mismatched_adapter_class", case_05_reject_mismatched_adapter_class),
        ("case_06_reject_invalid_source_artifact_type", case_06_reject_invalid_source_artifact_type),
        ("case_07_reject_invalid_adapter_status", case_07_reject_invalid_adapter_status),
        ("case_08_reject_invalid_runtime_mode", case_08_reject_invalid_runtime_mode),
        ("case_09_other_target_maps_to_correct_surface", case_09_other_target_maps_to_correct_surface),
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
from __future__ import annotations

from AI_GO.core.runtime.refinement.execution_fusion import (
    build_fused_execution_record,
)


def _valid_rosetta_state() -> dict:
    return {
        "artifact_type": "rosetta_runtime_execution_state",
        "sealed": True,
        "case_id": "CASE-73-001",
        "authorized_weight": 0.20,
        "refinement_entry_count": 2,
        "runtime_mode": "rosetta_refined_runtime",
        "downstream_status": "ready_for_child_core",
    }


def _valid_curved_mirror_state() -> dict:
    return {
        "artifact_type": "curved_mirror_runtime_execution_state",
        "sealed": True,
        "case_id": "CASE-73-001",
        "authorized_weight": 0.80,
        "refinement_entry_count": 1,
        "runtime_mode": "curved_mirror_refined_runtime",
        "downstream_status": "ready_for_child_core",
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_execution_fusion_record():
    result = build_fused_execution_record(
        _valid_rosetta_state(),
        _valid_curved_mirror_state(),
    )

    assert result["artifact_type"] == "execution_fusion_record"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-73-001"
    assert result["weights"]["rosetta_weight"] == 0.20
    assert result["weights"]["curved_mirror_weight"] == 0.80
    assert result["runtime_modes"]["rosetta_mode"] == "rosetta_refined_runtime"
    assert result["runtime_modes"]["curved_mirror_mode"] == "curved_mirror_refined_runtime"
    assert result["child_core_handoff"] == "fused_execution_ready"


def case_02_reject_invalid_rosetta_artifact_type():
    rosetta = _valid_rosetta_state()
    rosetta["artifact_type"] = "wrong_type"

    try:
        build_fused_execution_record(rosetta, _valid_curved_mirror_state())
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_invalid_curved_mirror_artifact_type():
    curved = _valid_curved_mirror_state()
    curved["artifact_type"] = "wrong_type"

    try:
        build_fused_execution_record(_valid_rosetta_state(), curved)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_unsealed_rosetta_state():
    rosetta = _valid_rosetta_state()
    rosetta["sealed"] = False

    try:
        build_fused_execution_record(rosetta, _valid_curved_mirror_state())
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_case_mismatch():
    curved = _valid_curved_mirror_state()
    curved["case_id"] = "CASE-OTHER"

    try:
        build_fused_execution_record(_valid_rosetta_state(), curved)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_combined_weight_over_one():
    rosetta = _valid_rosetta_state()
    curved = _valid_curved_mirror_state()
    rosetta["authorized_weight"] = 0.60
    curved["authorized_weight"] = 0.60

    try:
        build_fused_execution_record(rosetta, curved)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_invalid_rosetta_runtime_mode():
    rosetta = _valid_rosetta_state()
    rosetta["runtime_mode"] = "wrong_mode"

    try:
        build_fused_execution_record(rosetta, _valid_curved_mirror_state())
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_invalid_curved_mirror_runtime_mode():
    curved = _valid_curved_mirror_state()
    curved["runtime_mode"] = "wrong_mode"

    try:
        build_fused_execution_record(_valid_rosetta_state(), curved)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_zero_entry_support():
    rosetta = _valid_rosetta_state()
    curved = _valid_curved_mirror_state()
    rosetta["refinement_entry_count"] = 0
    curved["refinement_entry_count"] = 0

    result = build_fused_execution_record(rosetta, curved)
    assert result["entry_counts"]["rosetta_entries"] == 0
    assert result["entry_counts"]["curved_mirror_entries"] == 0


def case_10_reject_internal_field_leakage():
    rosetta = _valid_rosetta_state()
    rosetta["_debug"] = {"illegal": True}

    try:
        build_fused_execution_record(rosetta, _valid_curved_mirror_state())
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_execution_fusion_record", case_01_valid_execution_fusion_record),
        ("case_02_reject_invalid_rosetta_artifact_type", case_02_reject_invalid_rosetta_artifact_type),
        ("case_03_reject_invalid_curved_mirror_artifact_type", case_03_reject_invalid_curved_mirror_artifact_type),
        ("case_04_reject_unsealed_rosetta_state", case_04_reject_unsealed_rosetta_state),
        ("case_05_reject_case_mismatch", case_05_reject_case_mismatch),
        ("case_06_reject_combined_weight_over_one", case_06_reject_combined_weight_over_one),
        ("case_07_reject_invalid_rosetta_runtime_mode", case_07_reject_invalid_rosetta_runtime_mode),
        ("case_08_reject_invalid_curved_mirror_runtime_mode", case_08_reject_invalid_curved_mirror_runtime_mode),
        ("case_09_zero_entry_support", case_09_zero_entry_support),
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
from __future__ import annotations

from AI_GO.core.runtime.refinement.rosetta_runtime_application import (
    build_rosetta_runtime_execution_state,
)


def _valid_runtime_refinement_coupling_record() -> dict:
    return {
        "artifact_type": "runtime_refinement_coupling_record",
        "sealed": True,
        "case_id": "CASE-71-001",
        "allocation": {
            "rosetta_weight": 0.20,
            "curved_mirror_weight": 0.80,
        },
        "rosetta_channel": {
            "authorized_weight": 0.20,
            "route_target": "stage71_rosetta_runtime_application",
            "receipt_artifact_type": "rosetta_refinement_receipt",
            "entry_count": 2,
            "sealed_receipt": True,
        },
        "curved_mirror_channel": {
            "authorized_weight": 0.80,
            "route_target": "stage72_curved_mirror_runtime_application",
            "receipt_artifact_type": "curved_mirror_refinement_receipt",
            "entry_count": 1,
            "sealed_receipt": True,
        },
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_rosetta_runtime_execution_state():
    result = build_rosetta_runtime_execution_state(_valid_runtime_refinement_coupling_record())

    assert result["artifact_type"] == "rosetta_runtime_execution_state"
    assert result["sealed"] is True
    assert result["case_id"] == "CASE-71-001"
    assert result["authorized_weight"] == 0.20
    assert result["refinement_entry_count"] == 2
    assert result["runtime_mode"] == "rosetta_refined_runtime"
    assert result["downstream_status"] == "ready_for_child_core"


def case_02_reject_invalid_input_artifact_type():
    record = _valid_runtime_refinement_coupling_record()
    record["artifact_type"] = "wrong_type"

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_input():
    record = _valid_runtime_refinement_coupling_record()
    record["sealed"] = False

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_missing_rosetta_channel_field():
    record = _valid_runtime_refinement_coupling_record()
    del record["rosetta_channel"]["route_target"]

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_invalid_rosetta_route_target():
    record = _valid_runtime_refinement_coupling_record()
    record["rosetta_channel"]["route_target"] = "wrong_target"

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_invalid_rosetta_receipt_artifact_type():
    record = _valid_runtime_refinement_coupling_record()
    record["rosetta_channel"]["receipt_artifact_type"] = "wrong_type"

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_invalid_authorized_weight():
    record = _valid_runtime_refinement_coupling_record()
    record["rosetta_channel"]["authorized_weight"] = 1.5

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_cross_consumer_leakage():
    record = _valid_runtime_refinement_coupling_record()
    record["rosetta_channel"]["curved_mirror_signals"] = ["illegal"]

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_zero_entry_support():
    record = _valid_runtime_refinement_coupling_record()
    record["rosetta_channel"]["entry_count"] = 0

    result = build_rosetta_runtime_execution_state(record)
    assert result["refinement_entry_count"] == 0


def case_10_reject_internal_field_leakage():
    record = _valid_runtime_refinement_coupling_record()
    record["_debug"] = {"illegal": True}

    try:
        build_rosetta_runtime_execution_state(record)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_rosetta_runtime_execution_state", case_01_valid_rosetta_runtime_execution_state),
        ("case_02_reject_invalid_input_artifact_type", case_02_reject_invalid_input_artifact_type),
        ("case_03_reject_unsealed_input", case_03_reject_unsealed_input),
        ("case_04_reject_missing_rosetta_channel_field", case_04_reject_missing_rosetta_channel_field),
        ("case_05_reject_invalid_rosetta_route_target", case_05_reject_invalid_rosetta_route_target),
        ("case_06_reject_invalid_rosetta_receipt_artifact_type", case_06_reject_invalid_rosetta_receipt_artifact_type),
        ("case_07_reject_invalid_authorized_weight", case_07_reject_invalid_authorized_weight),
        ("case_08_reject_cross_consumer_leakage", case_08_reject_cross_consumer_leakage),
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
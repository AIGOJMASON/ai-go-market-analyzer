from __future__ import annotations

from copy import deepcopy

from AI_GO.core.runtime.refinement.runtime_refinement_coupler import (
    build_runtime_refinement_coupling_record,
)


def _valid_allocation() -> dict:
    return {
        "artifact_type": "engine_allocation_record",
        "sealed": True,
        "case_id": "CASE-70-001",
        "rosetta_weight": 0.20,
        "curved_mirror_weight": 0.80,
    }


def _valid_rosetta_receipt() -> dict:
    return {
        "artifact_type": "rosetta_refinement_receipt",
        "sealed": True,
        "case_id": "CASE-70-001",
        "entries": [
            {"guidance_id": "R-1", "signal": "compress_when_low_confidence"},
            {"guidance_id": "R-2", "signal": "preserve_human_facing_clarity"},
        ],
    }


def _valid_curved_mirror_receipt() -> dict:
    return {
        "artifact_type": "curved_mirror_refinement_receipt",
        "sealed": True,
        "case_id": "CASE-70-001",
        "entries": [
            {"signal_id": "C-1", "signal": "increase_structural_attention"},
        ],
    }


def _run_case(name: str, fn):
    try:
        fn()
        return {"case": name, "status": "passed"}
    except AssertionError:
        return {"case": name, "status": "failed"}
    except Exception:
        return {"case": name, "status": "failed"}


def case_01_valid_runtime_coupling_record():
    allocation = _valid_allocation()
    rosetta = _valid_rosetta_receipt()
    curved = _valid_curved_mirror_receipt()

    result = build_runtime_refinement_coupling_record(allocation, rosetta, curved)

    assert result["artifact_type"] == "runtime_refinement_coupling_record"
    assert result["sealed"] is True
    assert result["allocation"]["rosetta_weight"] == 0.20
    assert result["allocation"]["curved_mirror_weight"] == 0.80
    assert result["rosetta_channel"]["route_target"] == "stage71_rosetta_runtime_application"
    assert (
        result["curved_mirror_channel"]["route_target"]
        == "stage72_curved_mirror_runtime_application"
    )


def case_02_reject_invalid_allocation_artifact_type():
    allocation = _valid_allocation()
    allocation["artifact_type"] = "wrong_type"

    try:
        build_runtime_refinement_coupling_record(
            allocation,
            _valid_rosetta_receipt(),
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_03_reject_unsealed_allocation():
    allocation = _valid_allocation()
    allocation["sealed"] = False

    try:
        build_runtime_refinement_coupling_record(
            allocation,
            _valid_rosetta_receipt(),
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_04_reject_invalid_rosetta_receipt_type():
    rosetta = _valid_rosetta_receipt()
    rosetta["artifact_type"] = "wrong_type"

    try:
        build_runtime_refinement_coupling_record(
            _valid_allocation(),
            rosetta,
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_05_reject_invalid_curved_mirror_receipt_type():
    curved = _valid_curved_mirror_receipt()
    curved["artifact_type"] = "wrong_type"

    try:
        build_runtime_refinement_coupling_record(
            _valid_allocation(),
            _valid_rosetta_receipt(),
            curved,
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_06_reject_case_mismatch():
    curved = _valid_curved_mirror_receipt()
    curved["case_id"] = "CASE-OTHER"

    try:
        build_runtime_refinement_coupling_record(
            _valid_allocation(),
            _valid_rosetta_receipt(),
            curved,
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_07_reject_invalid_weight_range():
    allocation = _valid_allocation()
    allocation["rosetta_weight"] = 1.20

    try:
        build_runtime_refinement_coupling_record(
            allocation,
            _valid_rosetta_receipt(),
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_08_reject_cross_consumer_leakage_in_rosetta_receipt():
    rosetta = _valid_rosetta_receipt()
    rosetta["curved_mirror_signals"] = ["illegal"]

    try:
        build_runtime_refinement_coupling_record(
            _valid_allocation(),
            rosetta,
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def case_09_zero_entry_receipts_supported():
    rosetta = _valid_rosetta_receipt()
    curved = _valid_curved_mirror_receipt()
    rosetta["entries"] = []
    curved["entries"] = []

    result = build_runtime_refinement_coupling_record(
        _valid_allocation(),
        rosetta,
        curved,
    )

    assert result["rosetta_channel"]["entry_count"] == 0
    assert result["curved_mirror_channel"]["entry_count"] == 0


def case_10_reject_internal_field_leakage():
    allocation = _valid_allocation()
    allocation["_debug"] = {"note": "illegal"}

    try:
        build_runtime_refinement_coupling_record(
            allocation,
            _valid_rosetta_receipt(),
            _valid_curved_mirror_receipt(),
        )
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    cases = [
        ("case_01_valid_runtime_coupling_record", case_01_valid_runtime_coupling_record),
        (
            "case_02_reject_invalid_allocation_artifact_type",
            case_02_reject_invalid_allocation_artifact_type,
        ),
        ("case_03_reject_unsealed_allocation", case_03_reject_unsealed_allocation),
        (
            "case_04_reject_invalid_rosetta_receipt_type",
            case_04_reject_invalid_rosetta_receipt_type,
        ),
        (
            "case_05_reject_invalid_curved_mirror_receipt_type",
            case_05_reject_invalid_curved_mirror_receipt_type,
        ),
        ("case_06_reject_case_mismatch", case_06_reject_case_mismatch),
        ("case_07_reject_invalid_weight_range", case_07_reject_invalid_weight_range),
        (
            "case_08_reject_cross_consumer_leakage_in_rosetta_receipt",
            case_08_reject_cross_consumer_leakage_in_rosetta_receipt,
        ),
        ("case_09_zero_entry_receipts_supported", case_09_zero_entry_receipts_supported),
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
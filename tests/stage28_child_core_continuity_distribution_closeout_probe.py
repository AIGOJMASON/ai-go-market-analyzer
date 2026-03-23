from __future__ import annotations

from pprint import pprint

from AI_GO.core.child_flow.continuity_mutation import (
    process_continuity_mutation,
    reset_store,
)
from AI_GO.core.child_flow.continuity_distribution import (
    DistributionState,
    process_continuity_distribution,
)
from AI_GO.core.child_flow.continuity_distribution.continuity_distribution_registry import (
    CURRENT_DISTRIBUTION_POLICY_VERSION,
)


def _seed_store() -> None:
    reset_store()
    process_continuity_mutation(
        {
            "receipt_type": "continuity_intake_receipt",
            "intake_id": "INTAKE-DIST-001",
            "target_core": "louisville_gis_core",
            "continuity_scope": "child_core",
            "admission_basis": "critical_operational_failure",
            "watcher_receipt_ref": "state/receipts/watcher_receipt_dist_001.json",
            "output_disposition_ref": "state/receipts/output_disposition_dist_001.json",
            "runtime_ref": "state/runtime/runtime_receipt_dist_001.json",
            "policy_version": "stage26.v1",
            "timestamp": "2026-03-18T00:00:00Z",
        }
    )
    process_continuity_mutation(
        {
            "receipt_type": "continuity_intake_receipt",
            "intake_id": "INTAKE-DIST-002",
            "target_core": "louisville_gis_core",
            "continuity_scope": "child_core",
            "admission_basis": "policy_violation",
            "watcher_receipt_ref": "state/receipts/watcher_receipt_dist_002.json",
            "output_disposition_ref": "state/receipts/output_disposition_dist_002.json",
            "runtime_ref": "state/runtime/runtime_receipt_dist_002.json",
            "policy_version": "stage26.v1",
            "timestamp": "2026-03-19T00:00:00Z",
        }
    )


def _base_request() -> dict:
    return {
        "request_type": "continuity_read_request",
        "request_id": "READ-001",
        "requesting_surface": "pm_core",
        "consumer_profile": "pm_core_reader",
        "target_core": "louisville_gis_core",
        "continuity_scope": "child_core",
        "read_reason": "closeout probe",
        "requested_view": "latest_n_records",
        "policy_version": CURRENT_DISTRIBUTION_POLICY_VERSION,
        "timestamp": "2026-03-20T00:00:00Z",
    }


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_probe() -> dict:
    _seed_store()
    results = []

    def record(case_name: str, fn) -> None:
        try:
            fn()
            results.append({"case": case_name, "status": "passed"})
        except Exception as exc:
            results.append({"case": case_name, "status": "failed", "error": str(exc)})

    def case_01_valid_pm_profile_latest_n_records() -> None:
        request = _base_request()
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "fulfilled", f"expected fulfilled, got {result['status']}")
        _assert(result["artifact"]["artifact_type"] == "continuity_distribution_artifact", "wrong artifact type")
        _assert(result["receipt"]["receipt_type"] == "continuity_distribution_receipt", "wrong receipt type")
        _assert(result["artifact"]["consumer_profile"] == "pm_core_reader", "wrong consumer profile on artifact")
        _assert(result["artifact"]["record_count"] <= 5, "pm_core_reader should return at most five records")

    def case_02_valid_child_core_profile_latest_record() -> None:
        request = _base_request()
        request["request_id"] = "READ-002"
        request["requesting_surface"] = "child_core_reader"
        request["consumer_profile"] = "child_core_reader"
        request["requested_view"] = "latest_record"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "fulfilled", f"expected fulfilled, got {result['status']}")
        _assert(result["artifact"]["record_count"] <= 1, "child_core_reader latest_record should return at most one record")
        records = result["artifact"]["records"]
        for item in records:
            _assert("continuity_key" in item, "refs_only shaping missing continuity_key")
            _assert("watcher_receipt_ref" in item, "refs_only shaping missing watcher_receipt_ref")
            _assert("admission_basis" not in item, "child_core_reader should not receive admission_basis")

    def case_03_invalid_request_type() -> None:
        request = _base_request()
        request["request_id"] = "READ-003"
        request["request_type"] = "bad_request"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "invalid_input", "wrong rejection code")

    def case_04_invalid_consumer_profile() -> None:
        request = _base_request()
        request["request_id"] = "READ-004"
        request["consumer_profile"] = "unknown_profile"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "consumer_profile_unlawful", "wrong rejection code")

    def case_05_invalid_requester_for_profile() -> None:
        request = _base_request()
        request["request_id"] = "READ-005"
        request["requesting_surface"] = "forbidden_reader"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "requester_unlawful", "wrong rejection code")

    def case_06_invalid_target_for_profile() -> None:
        request = _base_request()
        request["request_id"] = "READ-006"
        request["target_core"] = "forbidden_core"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "target_unlawful", "wrong rejection code")

    def case_07_invalid_scope() -> None:
        request = _base_request()
        request["request_id"] = "READ-007"
        request["continuity_scope"] = "system"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "scope_unlawful", "wrong rejection code")

    def case_08_invalid_view_for_profile() -> None:
        request = _base_request()
        request["request_id"] = "READ-008"
        request["consumer_profile"] = "child_core_reader"
        request["requesting_surface"] = "child_core_reader"
        request["requested_view"] = "latest_n_records"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "view_unlawful", "wrong rejection code")

    def case_09_invalid_policy_version() -> None:
        request = _base_request()
        request["request_id"] = "READ-009"
        request["policy_version"] = "stage28.v999"
        result = process_continuity_distribution(request=request, state=DistributionState())
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert(result["receipt"]["rejection_code"] == "policy_version_invalid", "wrong rejection code")

    record("case_01_valid_pm_profile_latest_n_records", case_01_valid_pm_profile_latest_n_records)
    record("case_02_valid_child_core_profile_latest_record", case_02_valid_child_core_profile_latest_record)
    record("case_03_invalid_request_type", case_03_invalid_request_type)
    record("case_04_invalid_consumer_profile", case_04_invalid_consumer_profile)
    record("case_05_invalid_requester_for_profile", case_05_invalid_requester_for_profile)
    record("case_06_invalid_target_for_profile", case_06_invalid_target_for_profile)
    record("case_07_invalid_scope", case_07_invalid_scope)
    record("case_08_invalid_view_for_profile", case_08_invalid_view_for_profile)
    record("case_09_invalid_policy_version", case_09_invalid_policy_version)

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "stage": "Stage 28 — Continuity Distribution Boundary",
        "total_cases": len(results),
        "passed": passed,
        "failed": failed,
        "status": "passed" if failed == 0 else "failed",
        "results": results,
    }


if __name__ == "__main__":
    summary = run_probe()
    pprint(summary)
    if summary["failed"] > 0:
        raise SystemExit(1)
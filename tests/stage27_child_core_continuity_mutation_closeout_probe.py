from __future__ import annotations

from pprint import pprint

from AI_GO.core.child_flow.continuity_mutation import (
    process_continuity_mutation,
    reset_store,
)


def _base_receipt() -> dict:
    return {
        "receipt_type": "continuity_intake_receipt",
        "intake_id": "INTAKE-001",
        "target_core": "louisville_gis_core",
        "continuity_scope": "child_core",
        "admission_basis": "critical_operational_failure",
        "watcher_receipt_ref": "state/receipts/watcher_receipt_001.json",
        "output_disposition_ref": "state/receipts/output_disposition_001.json",
        "runtime_ref": "state/runtime/runtime_receipt_001.json",
        "policy_version": "stage26.v1",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_probe() -> dict:
    reset_store()
    results = []

    def record(case_name: str, fn) -> None:
        try:
            fn()
            results.append({"case": case_name, "status": "passed"})
        except Exception as exc:
            results.append({"case": case_name, "status": "failed", "error": str(exc)})

    def case_01_valid_created() -> None:
        receipt = _base_receipt()
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_receipt", "wrong receipt type")
        _assert(result["mutation_type"] == "created", "expected created")

    def case_02_duplicate_no_op() -> None:
        receipt = _base_receipt()
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_receipt", "wrong receipt type")
        _assert(result["mutation_type"] == "no_op", "expected no_op")

    def case_03_invalid_receipt_type() -> None:
        receipt = _base_receipt()
        receipt["receipt_type"] = "bad_receipt"
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_failure_receipt", "wrong failure receipt type")
        _assert(result["rejection_code"] == "invalid_input", "expected invalid_input")

    def case_04_invalid_target() -> None:
        receipt = _base_receipt()
        receipt["intake_id"] = "INTAKE-002"
        receipt["target_core"] = "forbidden_core"
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_failure_receipt", "wrong failure receipt type")
        _assert(result["rejection_code"] == "scope_unlawful", "expected scope_unlawful")

    def case_05_invalid_scope() -> None:
        receipt = _base_receipt()
        receipt["intake_id"] = "INTAKE-003"
        receipt["continuity_scope"] = "system"
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_failure_receipt", "wrong failure receipt type")
        _assert(result["rejection_code"] == "scope_unlawful", "expected scope_unlawful")

    def case_06_upstream_policy_mismatch() -> None:
        receipt = _base_receipt()
        receipt["intake_id"] = "INTAKE-004"
        receipt["policy_version"] = "stage26.v999"
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_failure_receipt", "wrong failure receipt type")
        _assert(result["rejection_code"] == "policy_version_invalid", "expected policy_version_invalid")

    def case_07_broken_lineage() -> None:
        receipt = _base_receipt()
        receipt["intake_id"] = "INTAKE-005"
        receipt["runtime_ref"] = ""
        result = process_continuity_mutation(receipt)
        _assert(result["receipt_type"] == "continuity_mutation_failure_receipt", "wrong failure receipt type")
        _assert(result["rejection_code"] == "lineage_broken", "expected lineage_broken")

    record("case_01_valid_created", case_01_valid_created)
    record("case_02_duplicate_no_op", case_02_duplicate_no_op)
    record("case_03_invalid_receipt_type", case_03_invalid_receipt_type)
    record("case_04_invalid_target", case_04_invalid_target)
    record("case_05_invalid_scope", case_05_invalid_scope)
    record("case_06_upstream_policy_mismatch", case_06_upstream_policy_mismatch)
    record("case_07_broken_lineage", case_07_broken_lineage)

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "stage": "Stage 27 — Continuity Mutation Boundary",
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
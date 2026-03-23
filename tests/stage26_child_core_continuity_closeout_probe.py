from __future__ import annotations

from copy import deepcopy
from pprint import pprint

from AI_GO.core.child_flow.continuity.child_core_continuity import (
    process_watcher_to_continuity,
)
from AI_GO.core.child_flow.continuity.continuity_registry import (
    CURRENT_POLICY_VERSION,
)
from AI_GO.core.child_flow.continuity.continuity_state import ContinuityState


def _base_context() -> dict:
    return {
        "target_core": "louisville_gis_core",
        "watcher_id": "WATCHER-LOUISVILLE-GIS-001",
        "watcher_receipt_ref": "state/receipts/watcher_receipt_001.json",
        "output_disposition_ref": "state/receipts/output_disposition_001.json",
        "runtime_ref": "state/runtime/runtime_receipt_001.json",
        "event_timestamp": "2026-03-18T21:00:00Z",
        "continuity_scope": "child_core",
        "intake_reason": "probe validation",
        "admission_policy_version": CURRENT_POLICY_VERSION,
    }


def _base_watcher_result() -> dict:
    return {
        "findings": {
            "critical_failure": True,
        },
        "findings_ref": "state/receipts/watcher_result_001.json",
    }


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_receipt_type(result: dict, expected_receipt_type: str) -> None:
    receipt = result["receipt"]
    _assert(receipt["receipt_type"] == expected_receipt_type, f"expected receipt_type={expected_receipt_type}, got {receipt['receipt_type']}")


def _assert_state_shape(state: dict) -> None:
    expected_keys = {
        "last_intake_id",
        "last_target_core",
        "last_disposition",
        "last_receipt_type",
        "last_receipt_ref",
        "last_timestamp",
    }
    _assert(set(state.keys()) == expected_keys, f"unexpected state keys: {sorted(state.keys())}")


def _assert_no_mutation_surface(result: dict) -> None:
    forbidden_top_level_keys = {
        "continuity_memory",
        "continuity_mutation",
        "memory_write",
        "publication",
        "delivery",
        "watcher_replay",
    }
    present = forbidden_top_level_keys.intersection(result.keys())
    _assert(not present, f"forbidden keys present in result: {sorted(present)}")


def _assert_findings_unchanged(original_watcher_result: dict, watcher_result_after: dict) -> None:
    _assert(
        watcher_result_after == original_watcher_result,
        "watcher_result was mutated by Stage 26",
    )


def run_probe() -> dict:
    results = []

    def record(case_name: str, fn) -> None:
        try:
            fn()
            results.append({"case": case_name, "status": "passed"})
        except Exception as exc:
            results.append({"case": case_name, "status": "failed", "error": str(exc)})

    def case_01_accepted() -> None:
        watcher_result = _base_watcher_result()
        original = deepcopy(watcher_result)
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "accepted", f"expected accepted, got {result['status']}")
        _assert_receipt_type(result, "continuity_intake_receipt")
        _assert(result["receipt"]["target_core"] == context["target_core"], "target_core not preserved")
        _assert(result["receipt"]["continuity_scope"] == context["continuity_scope"], "continuity_scope not preserved")
        _assert(result["receipt"]["policy_version"] == context["admission_policy_version"], "policy_version not preserved")
        _assert(result["state"]["last_disposition"] == "accepted", "state disposition not accepted")
        _assert_state_shape(result["state"])
        _assert_no_mutation_surface(result)
        _assert_findings_unchanged(original, watcher_result)

    def case_02_held() -> None:
        watcher_result = {
            "findings": {
                "repeated_signal": True,
            },
            "findings_ref": "state/receipts/watcher_result_hold.json",
        }
        original = deepcopy(watcher_result)
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "held", f"expected held, got {result['status']}")
        _assert_receipt_type(result, "continuity_hold_receipt")
        _assert("release_condition" in result["receipt"], "hold receipt missing release_condition")
        _assert("review_window" in result["receipt"], "hold receipt missing review_window")
        _assert(result["state"]["last_disposition"] == "held", "state disposition not held")
        _assert_state_shape(result["state"])
        _assert_no_mutation_surface(result)
        _assert_findings_unchanged(original, watcher_result)

    def case_03_rejected_insufficient_signal() -> None:
        watcher_result = {
            "findings": {
                "note_only": True,
            }
        }
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "insufficient_signal", "wrong rejection code")

    def case_04_rejected_malformed_watcher_result() -> None:
        watcher_result = {
            "findings_ref": "missing-findings.json",
        }
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "structural_invalid", "wrong rejection code")

    def case_05_rejected_invalid_context() -> None:
        watcher_result = _base_watcher_result()
        context = {
            "target_core": "louisville_gis_core",
        }
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "structural_invalid", "wrong rejection code")

    def case_06_rejected_broken_lineage() -> None:
        watcher_result = _base_watcher_result()
        context = _base_context()
        context["runtime_ref"] = ""
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "lineage_broken", "wrong rejection code for broken lineage")

    def case_07_rejected_unlawful_target_core() -> None:
        watcher_result = _base_watcher_result()
        context = _base_context()
        context["target_core"] = "forbidden_core"
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "scope_unlawful", "wrong rejection code")

    def case_08_rejected_unlawful_scope() -> None:
        watcher_result = _base_watcher_result()
        context = _base_context()
        context["continuity_scope"] = "system"
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "scope_unlawful", "wrong rejection code")

    def case_09_rejected_policy_version_mismatch() -> None:
        watcher_result = _base_watcher_result()
        context = _base_context()
        context["admission_policy_version"] = "stage26.v999"
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "policy_version_invalid", "wrong rejection code")

    def case_10_rejected_duplicate_event() -> None:
        watcher_result = {
            "findings": {
                "duplicate_event": True,
            }
        }
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "duplicate_event", "wrong rejection code")

    def case_11_rejected_stale_event() -> None:
        watcher_result = {
            "findings": {
                "stale_event": True,
            }
        }
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "stale_event", "wrong rejection code")

    def case_12_rejected_entropy_block() -> None:
        watcher_result = {
            "findings": {
                "entropy_block": True,
            }
        }
        context = _base_context()
        result = process_watcher_to_continuity(
            watcher_result=watcher_result,
            continuity_context=context,
            state=ContinuityState(),
        )
        _assert(result["status"] == "rejected", f"expected rejected, got {result['status']}")
        _assert_receipt_type(result, "continuity_failure_receipt")
        _assert(result["receipt"]["rejection_code"] == "entropy_block", "wrong rejection code")

    record("case_01_accepted", case_01_accepted)
    record("case_02_held", case_02_held)
    record("case_03_rejected_insufficient_signal", case_03_rejected_insufficient_signal)
    record("case_04_rejected_malformed_watcher_result", case_04_rejected_malformed_watcher_result)
    record("case_05_rejected_invalid_context", case_05_rejected_invalid_context)
    record("case_06_rejected_broken_lineage", case_06_rejected_broken_lineage)
    record("case_07_rejected_unlawful_target_core", case_07_rejected_unlawful_target_core)
    record("case_08_rejected_unlawful_scope", case_08_rejected_unlawful_scope)
    record("case_09_rejected_policy_version_mismatch", case_09_rejected_policy_version_mismatch)
    record("case_10_rejected_duplicate_event", case_10_rejected_duplicate_event)
    record("case_11_rejected_stale_event", case_11_rejected_stale_event)
    record("case_12_rejected_entropy_block", case_12_rejected_entropy_block)

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    summary = {
        "stage": "Stage 26 — Watcher to Continuity Intake Boundary",
        "total_cases": len(results),
        "passed": passed,
        "failed": failed,
        "status": "passed" if failed == 0 else "failed",
        "results": results,
    }
    return summary


if __name__ == "__main__":
    probe_summary = run_probe()
    pprint(probe_summary)

    if probe_summary["failed"] > 0:
        raise SystemExit(1)
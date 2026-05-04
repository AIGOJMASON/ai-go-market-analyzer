from __future__ import annotations

from pprint import pprint

from AI_GO.core.child_flow.continuity.child_core_continuity import (
    process_watcher_to_continuity,
)
from AI_GO.core.child_flow.continuity.continuity_registry import (
    CURRENT_POLICY_VERSION as STAGE26_POLICY_VERSION,
)
from AI_GO.core.child_flow.continuity.continuity_state import ContinuityState
from AI_GO.core.child_flow.continuity_mutation import (
    process_continuity_mutation,
    reset_store,
)
from AI_GO.core.child_flow.continuity_mutation.continuity_mutation_registry import (
    CURRENT_MUTATION_POLICY_VERSION as STAGE27_POLICY_VERSION,
)


def _base_context() -> dict:
    return {
        "target_core": "louisville_gis_core",
        "watcher_id": "WATCHER-LOUISVILLE-GIS-INTEGRATION-001",
        "watcher_receipt_ref": "state/receipts/watcher_receipt_integration_001.json",
        "output_disposition_ref": "state/receipts/output_disposition_integration_001.json",
        "runtime_ref": "state/runtime/runtime_receipt_integration_001.json",
        "event_timestamp": "2026-03-18T21:00:00Z",
        "continuity_scope": "child_core",
        "intake_reason": "stage26-stage27 integration probe",
        "admission_policy_version": STAGE26_POLICY_VERSION,
    }


def _accepted_watcher_result() -> dict:
    return {
        "findings": {
            "critical_failure": True,
        },
        "findings_ref": "state/receipts/watcher_result_integration_accepted.json",
    }


def _held_watcher_result() -> dict:
    return {
        "findings": {
            "repeated_signal": True,
        },
        "findings_ref": "state/receipts/watcher_result_integration_held.json",
    }


def _invalid_watcher_result() -> dict:
    return {
        "findings_ref": "state/receipts/watcher_result_integration_invalid.json",
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

    def case_01_happy_path_chain() -> None:
        stage26 = process_watcher_to_continuity(
            watcher_result=_accepted_watcher_result(),
            continuity_context=_base_context(),
            state=ContinuityState(),
        )

        _assert(stage26["status"] == "accepted", f"Stage 26 expected accepted, got {stage26['status']}")
        _assert(
            stage26["receipt"]["receipt_type"] == "continuity_intake_receipt",
            f"Stage 26 expected continuity_intake_receipt, got {stage26['receipt']['receipt_type']}",
        )

        stage27 = process_continuity_mutation(stage26["receipt"])

        _assert(
            stage27["receipt_type"] == "continuity_mutation_receipt",
            f"Stage 27 expected continuity_mutation_receipt, got {stage27['receipt_type']}",
        )
        _assert(
            stage27["mutation_type"] == "created",
            f"Stage 27 expected created, got {stage27['mutation_type']}",
        )
        _assert(
            stage27["upstream_policy_version"] == STAGE26_POLICY_VERSION,
            "Stage 27 did not preserve upstream intake policy version",
        )
        _assert(
            stage27["mutation_policy_version"] == STAGE27_POLICY_VERSION,
            "Stage 27 did not record its own mutation policy version correctly",
        )

    def case_02_duplicate_chain_rerun() -> None:
        stage26 = process_watcher_to_continuity(
            watcher_result=_accepted_watcher_result(),
            continuity_context={
                **_base_context(),
                "watcher_receipt_ref": "state/receipts/watcher_receipt_integration_002.json",
                "output_disposition_ref": "state/receipts/output_disposition_integration_002.json",
                "runtime_ref": "state/runtime/runtime_receipt_integration_002.json",
            },
            state=ContinuityState(),
        )

        _assert(stage26["status"] == "accepted", f"Stage 26 expected accepted, got {stage26['status']}")

        first = process_continuity_mutation(stage26["receipt"])
        second = process_continuity_mutation(stage26["receipt"])

        _assert(first["receipt_type"] == "continuity_mutation_receipt", "first Stage 27 result should be mutation receipt")
        _assert(first["mutation_type"] == "created", "first Stage 27 mutation should be created")
        _assert(second["receipt_type"] == "continuity_mutation_receipt", "second Stage 27 result should be mutation receipt")
        _assert(second["mutation_type"] == "no_op", "second Stage 27 mutation should be no_op")

    def case_03_hold_receipt_blocked() -> None:
        stage26 = process_watcher_to_continuity(
            watcher_result=_held_watcher_result(),
            continuity_context={
                **_base_context(),
                "watcher_receipt_ref": "state/receipts/watcher_receipt_integration_003.json",
                "output_disposition_ref": "state/receipts/output_disposition_integration_003.json",
                "runtime_ref": "state/runtime/runtime_receipt_integration_003.json",
            },
            state=ContinuityState(),
        )

        _assert(stage26["status"] == "held", f"Stage 26 expected held, got {stage26['status']}")
        _assert(
            stage26["receipt"]["receipt_type"] == "continuity_hold_receipt",
            f"Stage 26 expected continuity_hold_receipt, got {stage26['receipt']['receipt_type']}",
        )

        stage27 = process_continuity_mutation(stage26["receipt"])

        _assert(
            stage27["receipt_type"] == "continuity_mutation_failure_receipt",
            f"Stage 27 expected continuity_mutation_failure_receipt, got {stage27['receipt_type']}",
        )
        _assert(
            stage27["rejection_code"] == "invalid_input",
            f"Stage 27 expected invalid_input, got {stage27['rejection_code']}",
        )

    def case_04_failure_receipt_blocked() -> None:
        stage26 = process_watcher_to_continuity(
            watcher_result=_invalid_watcher_result(),
            continuity_context={
                **_base_context(),
                "watcher_receipt_ref": "state/receipts/watcher_receipt_integration_004.json",
                "output_disposition_ref": "state/receipts/output_disposition_integration_004.json",
                "runtime_ref": "state/runtime/runtime_receipt_integration_004.json",
            },
            state=ContinuityState(),
        )

        _assert(stage26["status"] == "rejected", f"Stage 26 expected rejected, got {stage26['status']}")
        _assert(
            stage26["receipt"]["receipt_type"] == "continuity_failure_receipt",
            f"Stage 26 expected continuity_failure_receipt, got {stage26['receipt']['receipt_type']}",
        )

        stage27 = process_continuity_mutation(stage26["receipt"])

        _assert(
            stage27["receipt_type"] == "continuity_mutation_failure_receipt",
            f"Stage 27 expected continuity_mutation_failure_receipt, got {stage27['receipt_type']}",
        )
        _assert(
            stage27["rejection_code"] == "invalid_input",
            f"Stage 27 expected invalid_input, got {stage27['rejection_code']}",
        )

    record("case_01_happy_path_chain", case_01_happy_path_chain)
    record("case_02_duplicate_chain_rerun", case_02_duplicate_chain_rerun)
    record("case_03_hold_receipt_blocked", case_03_hold_receipt_blocked)
    record("case_04_failure_receipt_blocked", case_04_failure_receipt_blocked)

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "stage": "Stage 26 → Stage 27 Integration",
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
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from child_cores.runtime.child_core_runtime import handoff_ingress_to_runtime
from child_cores.runtime.runtime_state import RuntimeState


def build_valid_ingress_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "ingress_receipt",
        "ingress_id": "INGRESS-TEST-001",
        "source_dispatch_id": "DISPATCH-TEST-001",
        "source_decision_id": "PM-DECISION-TEST-001",
        "target_core": "contractor_proposals_core",
        "destination_surface": "execution.ingress_processor",
        "handoff_status": "accepted",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_ingress_not_accepted_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "ingress_receipt",
        "ingress_id": "INGRESS-TEST-002",
        "source_dispatch_id": "DISPATCH-TEST-002",
        "source_decision_id": "PM-DECISION-TEST-002",
        "target_core": "contractor_proposals_core",
        "destination_surface": "execution.ingress_processor",
        "handoff_status": "rejected",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_unknown_target_ingress_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "ingress_receipt",
        "ingress_id": "INGRESS-TEST-003",
        "source_dispatch_id": "DISPATCH-TEST-003",
        "source_decision_id": "PM-DECISION-TEST-003",
        "target_core": "unknown_core",
        "destination_surface": "execution.ingress_processor",
        "handoff_status": "accepted",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def build_surface_mismatch_ingress_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "ingress_receipt",
        "ingress_id": "INGRESS-TEST-004",
        "source_dispatch_id": "DISPATCH-TEST-004",
        "source_decision_id": "PM-DECISION-TEST-004",
        "target_core": "louisville_gis_core",
        "destination_surface": "execution.ingress_processor",
        "handoff_status": "accepted",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage22_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    execution_surface_map: Mapping[str, str] = {
        "contractor_proposals_core": "execution.ingress_processor",
        "louisville_gis_core": "execution.gis_processor",
    }

    runtime_context_valid: Dict[str, Any] = {
        "execution_surface": "execution.ingress_processor",
        "input_refs": ["INPUT-REF-001"],
    }

    runtime_context_gis_mismatch: Dict[str, Any] = {
        "execution_surface": "execution.ingress_processor",
    }

    handler_calls: List[Dict[str, Any]] = []

    def contractor_runtime_handler(
        ingress_receipt: Dict[str, Any],
        runtime_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        handler_calls.append(
            {
                "target_core": ingress_receipt["target_core"],
                "ingress_id": ingress_receipt["ingress_id"],
                "execution_surface": runtime_context["execution_surface"],
            }
        )
        return {"result_ref": "RESULT-REF-001"}

    execution_handler_map = {
        "contractor_proposals_core": contractor_runtime_handler,
        # intentionally omit louisville_gis_core for negative test
    }

    state = RuntimeState()
    results: Dict[str, Any] = {}

    # TEST 1: Valid runtime start
    receipt1 = build_valid_ingress_receipt()
    result1 = handoff_ingress_to_runtime(
        ingress_receipt=receipt1,
        runtime_context=runtime_context_valid,
        valid_child_core_ids=valid_child_cores,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
        state=state,
    )
    results["test_valid_runtime_start"] = {
        "passed": result1.get("artifact_type") == "runtime_receipt"
        and result1.get("target_core") == "contractor_proposals_core"
        and result1.get("execution_surface") == "execution.ingress_processor"
        and result1.get("result_ref") == "RESULT-REF-001"
        and len(handler_calls) == 1
        and handler_calls[0]["ingress_id"] == "INGRESS-TEST-001",
        "artifact": result1,
    }

    # TEST 2: Ingress not accepted fails
    receipt2 = build_ingress_not_accepted_receipt()
    result2 = handoff_ingress_to_runtime(
        ingress_receipt=receipt2,
        runtime_context=runtime_context_valid,
        valid_child_core_ids=valid_child_cores,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
        state=state,
    )
    results["test_ingress_not_accepted_fails"] = {
        "passed": result2.get("artifact_type") == "runtime_failure_receipt"
        and result2.get("reason") == "ingress_not_accepted",
        "artifact": result2,
    }

    # TEST 3: Unknown target core fails
    receipt3 = build_unknown_target_ingress_receipt()
    result3 = handoff_ingress_to_runtime(
        ingress_receipt=receipt3,
        runtime_context=runtime_context_valid,
        valid_child_core_ids=valid_child_cores,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
        state=state,
    )
    results["test_unknown_target_core_fails"] = {
        "passed": result3.get("artifact_type") == "runtime_failure_receipt"
        and result3.get("reason") == "unknown_target_core",
        "artifact": result3,
    }

    # TEST 4: Execution-surface mismatch fails
    receipt4 = build_surface_mismatch_ingress_receipt()
    result4 = handoff_ingress_to_runtime(
        ingress_receipt=receipt4,
        runtime_context=runtime_context_gis_mismatch,
        valid_child_core_ids=valid_child_cores,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
        state=state,
    )
    results["test_execution_surface_mismatch_fails"] = {
        "passed": result4.get("artifact_type") == "runtime_failure_receipt"
        and result4.get("reason") == "execution_surface_target_mismatch",
        "artifact": result4,
    }

    # TEST 5: Missing execution handler fails
    receipt5 = {
        "artifact_type": "ingress_receipt",
        "ingress_id": "INGRESS-TEST-005",
        "source_dispatch_id": "DISPATCH-TEST-005",
        "source_decision_id": "PM-DECISION-TEST-005",
        "target_core": "louisville_gis_core",
        "destination_surface": "execution.gis_processor",
        "handoff_status": "accepted",
        "timestamp": "2026-03-18T00:00:00Z",
    }
    runtime_context5 = {
        "execution_surface": "execution.gis_processor",
    }
    result5 = handoff_ingress_to_runtime(
        ingress_receipt=receipt5,
        runtime_context=runtime_context5,
        valid_child_core_ids=valid_child_cores,
        execution_surface_map=execution_surface_map,
        execution_handler_map=execution_handler_map,
        state=state,
    )
    results["test_missing_execution_handler_fails"] = {
        "passed": result5.get("artifact_type") == "runtime_failure_receipt"
        and result5.get("reason") == "missing_execution_handler",
        "artifact": result5,
    }

    # TEST 6: No output / watcher / continuity leakage
    leak_keys = [
        "final_output",
        "child_core_output",
        "watcher_status",
        "continuity_update",
        "smi_update",
    ]
    leak_present = any(key in result1 for key in leak_keys)
    results["test_no_output_or_monitoring_leakage"] = {
        "passed": leak_present is False
    }

    # TEST 7: Exact minimal state shape
    results["test_state_minimal_exact"] = {
        "passed": set(vars(state).keys()) == {
            "last_runtime_id",
            "last_target_core",
            "last_timestamp",
        }
    }

    return {
        "stage": "STAGE_22_CLOSEOUT",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    output = run_stage22_closeout_probe()
    import json
    print(json.dumps(output, indent=2))
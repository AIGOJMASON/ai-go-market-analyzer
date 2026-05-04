from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

from AI_GO.child_cores.output.child_core_output import handoff_runtime_to_output
from AI_GO.child_cores.output.output_registry import DECLARED_OUTPUT_SURFACES
from AI_GO.child_cores.output.output_state import OutputState


def build_valid_runtime_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "runtime_receipt",
        "runtime_id": "RUNTIME-OUT-001",
        "source_ingress_id": "INGRESS-OUT-001",
        "source_dispatch_id": "DISPATCH-OUT-001",
        "source_decision_id": "PM-DECISION-OUT-001",
        "target_core": "contractor_proposals_core",
        "execution_surface": "execution.ingress_processor",
        "runtime_status": "completed",
        "result_ref": "RESULT-REF-OUT-001",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage23_child_core_output_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    output_context_valid: Dict[str, Any] = {
        "output_surface": "output.proposal_artifact",
        "output_flags": ["bounded"],
        "input_refs": ["INPUT-REF-OUT-001"],
    }

    state = OutputState()
    results: Dict[str, Any] = {}

    def valid_builder(
        runtime_receipt: Dict[str, Any],
        output_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "payload": {
                "target_core": runtime_receipt["target_core"],
                "runtime_id": runtime_receipt["runtime_id"],
                "result_ref": runtime_receipt["result_ref"],
                "output_flags": output_context.get("output_flags", []),
            }
        }

    def bad_type_builder(
        runtime_receipt: Dict[str, Any],
        output_context: Dict[str, Any],
    ) -> str:
        return "not-a-dict"

    def crashing_builder(
        runtime_receipt: Dict[str, Any],
        output_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise RuntimeError("forced output crash")

    # TEST 1: valid output handoff
    result1 = handoff_runtime_to_output(
        runtime_receipt=build_valid_runtime_receipt(),
        output_context=output_context_valid,
        valid_child_core_ids=valid_child_cores,
        output_surface_map=DECLARED_OUTPUT_SURFACES,
        output_builder_map={"contractor_proposals_core": valid_builder},
        state=state,
    )
    results["test_valid_output_handoff"] = {
        "passed": (
            isinstance(result1, dict)
            and "output_artifact" in result1
            and "output_receipt" in result1
            and result1["output_artifact"].get("artifact_type") == "output_artifact"
            and result1["output_receipt"].get("artifact_type") == "output_receipt"
        ),
        "artifact": result1,
    }

    # TEST 2: runtime not completed rejected
    invalid_runtime = build_valid_runtime_receipt()
    invalid_runtime["runtime_status"] = "failed"
    result2 = handoff_runtime_to_output(
        runtime_receipt=invalid_runtime,
        output_context=output_context_valid,
        valid_child_core_ids=valid_child_cores,
        output_surface_map=DECLARED_OUTPUT_SURFACES,
        output_builder_map={"contractor_proposals_core": valid_builder},
        state=state,
    )
    results["test_runtime_not_completed_rejected"] = {
        "passed": (
            result2.get("artifact_type") == "output_failure_receipt"
            and result2.get("reason") == "runtime_not_completed"
        ),
        "artifact": result2,
    }

    # TEST 3: bad builder type contained
    result3 = handoff_runtime_to_output(
        runtime_receipt=build_valid_runtime_receipt(),
        output_context=output_context_valid,
        valid_child_core_ids=valid_child_cores,
        output_surface_map=DECLARED_OUTPUT_SURFACES,
        output_builder_map={"contractor_proposals_core": bad_type_builder},
        state=state,
    )
    results["test_invalid_builder_result_type_contained"] = {
        "passed": (
            result3.get("artifact_type") == "output_failure_receipt"
            and result3.get("reason") == "invalid_builder_result_type"
        ),
        "artifact": result3,
    }

    # TEST 4: builder exception contained
    result4 = handoff_runtime_to_output(
        runtime_receipt=build_valid_runtime_receipt(),
        output_context=output_context_valid,
        valid_child_core_ids=valid_child_cores,
        output_surface_map=DECLARED_OUTPUT_SURFACES,
        output_builder_map={"contractor_proposals_core": crashing_builder},
        state=state,
    )
    results["test_output_builder_exception_contained"] = {
        "passed": (
            result4.get("artifact_type") == "output_failure_receipt"
            and result4.get("reason") == "output_builder_exception:RuntimeError"
        ),
        "artifact": result4,
    }

    # TEST 5: no watcher leakage in output
    valid_output = result1.get("output_artifact", {})
    results["test_no_watcher_or_continuity_leakage"] = {
        "passed": (
            "watcher" not in valid_output
            and "continuity" not in valid_output
            and "publication" not in valid_output
        ),
        "artifact": valid_output,
    }

    # TEST 6: minimal state shape
    results["test_minimal_output_state_shape"] = {
        "passed": set(state.__dict__.keys()) == {
            "last_output_id",
            "last_target_core",
            "last_timestamp",
        },
        "artifact": dict(state.__dict__),
    }

    return {
        "stage": "STAGE_23_CHILD_CORE_OUTPUT_CLOSEOUT_PROBE",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_stage23_child_core_output_closeout_probe(), indent=2))
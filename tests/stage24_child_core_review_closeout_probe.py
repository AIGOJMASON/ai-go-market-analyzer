from __future__ import annotations

import json
from typing import Any, Dict, List

from AI_GO.child_cores.review.child_core_review import handoff_output_to_review
from AI_GO.child_cores.review.review_registry import (
    ALLOWED_DOWNSTREAM_TARGETS,
    DEFAULT_TARGETS,
)
from AI_GO.child_cores.review.review_state import ReviewState


def build_valid_output_artifact() -> Dict[str, Any]:
    return {
        "artifact_type": "output_artifact",
        "stage": "stage23_child_core_output",
        "output_id": "OUTPUT-CONTRACTOR_PROPOSALS_CORE-RUNTIME-001",
        "source_runtime_id": "RUNTIME-001",
        "source_ingress_id": "INGRESS-001",
        "source_dispatch_id": "DISPATCH-001",
        "source_decision_id": "PM-DECISION-001",
        "target_core": "contractor_proposals_core",
        "output_surface": "output.proposal_artifact",
        "output_status": "constructed",
        "payload": {
            "runtime_id": "RUNTIME-001",
            "result_ref": "RESULT-001",
        },
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage24_child_core_review_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    state = ReviewState()
    results: Dict[str, Any] = {}

    # TEST 1: valid review routing to watcher intake
    result1 = handoff_output_to_review(
        output_artifact=build_valid_output_artifact(),
        review_context={"requested_target": "watcher_intake"},
        valid_child_core_ids=valid_child_cores,
        allowed_downstream_targets=ALLOWED_DOWNSTREAM_TARGETS,
        default_targets=DEFAULT_TARGETS,
        state=state,
    )
    results["test_valid_route_to_watcher_target"] = {
        "passed": (
            result1.get("artifact_type") == "output_disposition_receipt"
            and result1.get("selected_target") == "watcher_intake"
            and result1.get("disposition_status") == "routed"
        ),
        "artifact": result1,
    }

    # TEST 2: output not constructed rejected
    invalid_output = build_valid_output_artifact()
    invalid_output["output_status"] = "failed"
    result2 = handoff_output_to_review(
        output_artifact=invalid_output,
        review_context={"requested_target": "watcher_intake"},
        valid_child_core_ids=valid_child_cores,
        allowed_downstream_targets=ALLOWED_DOWNSTREAM_TARGETS,
        default_targets=DEFAULT_TARGETS,
        state=state,
    )
    results["test_output_not_constructed_rejected"] = {
        "passed": (
            result2.get("artifact_type") == "review_failure_receipt"
            and result2.get("reason") == "output_not_constructed"
        ),
        "artifact": result2,
    }

    # TEST 3: explicit hold path
    result3 = handoff_output_to_review(
        output_artifact=build_valid_output_artifact(),
        review_context={"requested_target": "manual_review_queue", "review_flags": ["hold"]},
        valid_child_core_ids=valid_child_cores,
        allowed_downstream_targets=ALLOWED_DOWNSTREAM_TARGETS,
        default_targets=DEFAULT_TARGETS,
        state=state,
    )
    results["test_hold_receipt_emitted"] = {
        "passed": (
            result3.get("artifact_type") == "review_hold_receipt"
            and result3.get("propagation_status") == "held"
        ),
        "artifact": result3,
    }

    # TEST 4: route override fallback to default target
    result4 = handoff_output_to_review(
        output_artifact=build_valid_output_artifact(),
        review_context={
            "requested_target": "watcher_intake",
            "route_overrides": {"contractor_proposals_core": "invalid_target"},
        },
        valid_child_core_ids=valid_child_cores,
        allowed_downstream_targets=ALLOWED_DOWNSTREAM_TARGETS,
        default_targets=DEFAULT_TARGETS,
        state=state,
    )
    results["test_invalid_override_falls_back_to_default"] = {
        "passed": (
            result4.get("artifact_type") == "output_disposition_receipt"
            and result4.get("selected_target") == DEFAULT_TARGETS["contractor_proposals_core"]
        ),
        "artifact": result4,
    }

    # TEST 5: no watcher execution leakage
    results["test_no_watcher_execution_leakage"] = {
        "passed": (
            "watcher_result" not in result1
            and "watcher_state" not in result1
            and "continuity" not in result1
            and "publication" not in result1
        ),
        "artifact": result1,
    }

    # TEST 6: minimal state shape
    results["test_minimal_review_state_shape"] = {
        "passed": set(state.__dict__.keys()) == {
            "last_review_id",
            "last_target_core",
            "last_disposition",
            "last_timestamp",
        },
        "artifact": dict(state.__dict__),
    }

    return {
        "stage": "STAGE_24_CHILD_CORE_REVIEW_CLOSEOUT_PROBE",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_stage24_child_core_review_closeout_probe(), indent=2))
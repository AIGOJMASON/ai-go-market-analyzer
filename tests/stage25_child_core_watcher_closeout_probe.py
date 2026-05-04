from __future__ import annotations

import json
from typing import Any, Dict, List

from AI_GO.child_cores.watcher.child_core_watcher import handoff_review_to_watcher
from AI_GO.child_cores.watcher.watcher_registry import (
    DECLARED_WATCHER_TARGET,
    WATCHER_HANDLERS,
)
from AI_GO.child_cores.watcher.watcher_state import WatcherState


def build_valid_disposition_receipt() -> Dict[str, Any]:
    return {
        "artifact_type": "output_disposition_receipt",
        "stage": "stage24_child_core_review",
        "review_id": "REVIEW-CONTRACTOR_PROPOSALS_CORE-OUTPUT-001",
        "source_output_id": "OUTPUT-CONTRACTOR_PROPOSALS_CORE-RUNTIME-001",
        "source_runtime_id": "RUNTIME-001",
        "target_core": "contractor_proposals_core",
        "requested_target": "watcher_intake",
        "selected_target": "watcher_intake",
        "disposition_status": "routed",
        "timestamp": "2026-03-18T00:00:00Z",
    }


def run_stage25_child_core_watcher_closeout_probe() -> Dict[str, Any]:
    valid_child_cores: List[str] = [
        "contractor_proposals_core",
        "louisville_gis_core",
    ]

    state = WatcherState()
    results: Dict[str, Any] = {}

    # TEST 1: valid watcher handoff
    result1 = handoff_review_to_watcher(
        disposition_receipt=build_valid_disposition_receipt(),
        watcher_context={"watcher_flags": ["bounded"]},
        valid_child_core_ids=valid_child_cores,
        watcher_target=DECLARED_WATCHER_TARGET,
        watcher_handler_map=WATCHER_HANDLERS,
        state=state,
    )
    results["test_valid_watcher_handoff"] = {
        "passed": (
            isinstance(result1, dict)
            and "watcher_result" in result1
            and "watcher_receipt" in result1
            and result1["watcher_result"].get("artifact_type") == "watcher_result"
            and result1["watcher_receipt"].get("artifact_type") == "watcher_receipt"
        ),
        "artifact": result1,
    }

    # TEST 2: wrong selected target rejected
    invalid_target = build_valid_disposition_receipt()
    invalid_target["selected_target"] = "manual_review_queue"
    result2 = handoff_review_to_watcher(
        disposition_receipt=invalid_target,
        watcher_context={},
        valid_child_core_ids=valid_child_cores,
        watcher_target=DECLARED_WATCHER_TARGET,
        watcher_handler_map=WATCHER_HANDLERS,
        state=state,
    )
    results["test_wrong_selected_target_rejected"] = {
        "passed": (
            result2.get("artifact_type") == "watcher_failure_receipt"
            and result2.get("reason") == "selected_target_not_watcher"
        ),
        "artifact": result2,
    }

    # TEST 3: watcher handler exception contained
    def crashing_handler(
        disposition_receipt: Dict[str, Any],
        watcher_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise RuntimeError("forced watcher crash")

    result3 = handoff_review_to_watcher(
        disposition_receipt=build_valid_disposition_receipt(),
        watcher_context={},
        valid_child_core_ids=valid_child_cores,
        watcher_target=DECLARED_WATCHER_TARGET,
        watcher_handler_map={"contractor_proposals_core": crashing_handler},
        state=state,
    )
    results["test_watcher_handler_exception_contained"] = {
        "passed": (
            result3.get("artifact_type") == "watcher_failure_receipt"
            and result3.get("reason") == "watcher_handler_exception:RuntimeError"
        ),
        "artifact": result3,
    }

    # TEST 4: invalid watcher result type contained
    def bad_type_handler(
        disposition_receipt: Dict[str, Any],
        watcher_context: Dict[str, Any],
    ) -> str:
        return "not-a-dict"

    result4 = handoff_review_to_watcher(
        disposition_receipt=build_valid_disposition_receipt(),
        watcher_context={},
        valid_child_core_ids=valid_child_cores,
        watcher_target=DECLARED_WATCHER_TARGET,
        watcher_handler_map={"contractor_proposals_core": bad_type_handler},
        state=state,
    )
    results["test_invalid_watcher_result_type_contained"] = {
        "passed": (
            result4.get("artifact_type") == "watcher_failure_receipt"
            and result4.get("reason") == "invalid_watcher_result_type"
        ),
        "artifact": result4,
    }

    # TEST 5: no continuity or publication leakage
    valid_result = result1.get("watcher_result", {})
    results["test_no_continuity_or_publication_leakage"] = {
        "passed": (
            "continuity" not in valid_result
            and "publication" not in valid_result
            and "delivery" not in valid_result
        ),
        "artifact": valid_result,
    }

    # TEST 6: minimal state shape
    results["test_minimal_watcher_state_shape"] = {
        "passed": set(state.__dict__.keys()) == {
            "last_watcher_id",
            "last_target_core",
            "last_watcher_status",
            "last_timestamp",
        },
        "artifact": dict(state.__dict__),
    }

    return {
        "stage": "STAGE_25_CHILD_CORE_WATCHER_CLOSEOUT_PROBE",
        "status": "complete",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_stage25_child_core_watcher_closeout_probe(), indent=2))
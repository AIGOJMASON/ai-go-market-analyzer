from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.child_cores.contractor_builder_v1.api.schemas.contractor_builder_response import (
    build_contractor_builder_response,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _base_payload() -> Dict[str, Any]:
    return {
        "status": "ok",
        "request_id": "contractor-live-001",
        "route_mode": "pm_route_live",
        "input_mode": "live",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "receipt_id": "rcpt_contractor_live_001",
        "watcher_validation_id": "watcher_contractor_live_001",
        "closeout_id": "closeout_contractor_live_001",
        "closeout_status": "accepted",
        "requires_review": False,
        "governance_panel": {
            "watcher_passed": True,
        },
        "case_panel": {
            "case_id": "contractor-live-001",
            "title": "Interior kitchen refresh with cabinet, lighting, and minor layout planning.",
            "observed_at": None,
        },
        "runtime_panel": {
            "project_class": "remodel",
            "trade_profile": "interior",
            "complexity_level": "medium",
            "location_mode": "remote",
            "scope_summary": "Interior kitchen refresh with cabinet, lighting, and minor layout planning.",
            "candidate_count": 1,
            "candidates": ["interior_package_v1"],
        },
        "recommendation_panel": {
            "recommendations": [
                {
                    "package_id": "interior_package_v1",
                    "title": "Interior Planning Package",
                    "rationale": "Aligned to remodel scope with near_term timeline.",
                    "confidence": "medium",
                }
            ]
        },
        "refinement_panel": {
            "signal": "scope_alignment_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Scope, trade, and timeline support a planning package recommendation.",
            "narrative": "Governed output remains advisory and non-executing.",
        },
        "pm_strategy_record": {
            "strategy_class": "reinforced_support",
            "continuity_strength": "medium",
            "trend_direction": "up",
            "posture": "supportive",
        },
        "pm_review_record": {
            "review_class": "plan",
            "review_priority": "medium",
        },
        "pm_planning_record": {
            "plan_class": "prepare_plan",
            "next_step_class": "prepare_plan",
            "plan_priority": "medium",
        },
        "pm_queue_record": {
            "queue_lane": "planning",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "medium",
        },
        "pm_workflow_dispatch_record": {
            "dispatch_class": "planning_dispatch",
            "dispatch_target": "pm_planning",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
    }


def case_01_system_view_top_level_shape() -> None:
    response = build_contractor_builder_response(_base_payload()).model_dump(by_alias=True)
    expected = {"case", "runtime", "recommendation", "cognition", "pm_workflow", "governance"}
    _assert(set(response["system_view"].keys()) == expected, "system_view shape mismatch")


def case_02_runtime_projection() -> None:
    response = build_contractor_builder_response(_base_payload()).model_dump(by_alias=True)
    runtime = response["system_view"]["runtime"]
    _assert(runtime["project_class"] == "remodel", "project_class mismatch")
    _assert(runtime["trade_profile"] == "interior", "trade_profile mismatch")
    _assert(runtime["candidate_count"] == 1, "candidate_count mismatch")


def case_03_recommendation_present() -> None:
    response = build_contractor_builder_response(_base_payload()).model_dump(by_alias=True)
    recommendation = response["system_view"]["recommendation"]
    _assert(recommendation["state"] == "present", "recommendation should be present")
    _assert(recommendation["count"] == 1, "recommendation count mismatch")


def case_04_cognition_visible() -> None:
    response = build_contractor_builder_response(_base_payload()).model_dump(by_alias=True)
    refinement = response["system_view"]["cognition"]["refinement"]
    _assert(refinement["state"] == "present", "refinement should be present")
    _assert(refinement["signal"] == "scope_alignment_confirmed", "refinement signal mismatch")


def case_05_pm_workflow_collapsed_surface() -> None:
    response = build_contractor_builder_response(_base_payload()).model_dump(by_alias=True)
    workflow = response["system_view"]["pm_workflow"]
    _assert(workflow["state"] == "present", "pm_workflow should be present")
    _assert(workflow["strategy"]["class"] == "reinforced_support", "strategy class mismatch")
    _assert(workflow["dispatch"]["ready"] is True, "dispatch ready mismatch")


def case_06_rejected_shape_stable() -> None:
    payload = _base_payload()
    payload["recommendation_panel"] = {"recommendations": []}
    payload["rejection_panel"] = {"reason": "insufficient confirmation for package recommendation"}

    response = build_contractor_builder_response(payload).model_dump(by_alias=True)
    recommendation = response["system_view"]["recommendation"]
    _assert(recommendation["state"] == "rejected", "rejection state mismatch")
    _assert(recommendation["summary"] == "insufficient confirmation for package recommendation", "rejection summary mismatch")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_system_view_top_level_shape", case_01_system_view_top_level_shape),
    ("case_02_runtime_projection", case_02_runtime_projection),
    ("case_03_recommendation_present", case_03_recommendation_present),
    ("case_04_cognition_visible", case_04_cognition_visible),
    ("case_05_pm_workflow_collapsed_surface", case_05_pm_workflow_collapsed_surface),
    ("case_06_rejected_shape_stable", case_06_rejected_shape_stable),
]


def run_probe() -> Dict[str, Any]:
    results: List[Dict[str, str]] = []
    passed = 0
    failed = 0

    for case_name, case_fn in TEST_CASES:
        try:
            case_fn()
            results.append({"case": case_name, "status": "passed"})
            passed += 1
        except Exception as exc:  # noqa: BLE001
            results.append({"case": case_name, "status": "failed", "error": str(exc)})
            failed += 1

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())
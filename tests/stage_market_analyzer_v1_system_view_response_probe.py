from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _base_payload() -> Dict[str, Any]:
    return {
        "status": "ok",
        "request_id": "live-b3-002",
        "route_mode": "pm_route_live",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "receipt_id": "rcpt_market_analyzer_v1_20260325T120000Z_abc123",
        "watcher_validation_id": "watcher_market_analyzer_v1_20260325T120000Z_def456",
        "closeout_id": "closeout_market_analyzer_v1_20260325T120000Z_ghi789",
        "closeout_status": "accepted",
        "requires_review": False,
        "governance_panel": {
            "watcher_passed": True,
        },
        "case_panel": {
            "case_id": "live-b3-002",
            "title": "Retail momentum surges on speculative chatter",
            "observed_at": None,
        },
        "market_panel": {
            "market_regime": "normal",
            "event_theme": "speculative_move",
            "macro_bias": "mixed",
            "headline": "Retail momentum surges on speculative chatter",
        },
        "candidate_panel": {
            "candidate_count": 0,
            "symbols": [],
        },
        "recommendation_panel": {
            "recommendation_count": 0,
            "recommendations": [],
        },
        "refinement_panel": {
            "signal": "speculative_signal_detected",
            "confidence_adjustment": "down",
            "risk_flag": "low_confirmation",
            "insight": "Speculative move lacks necessity support.",
            "narrative": "Signal present, but confidence reduced due to weak confirmation.",
        },
        "pm_strategy_record": {
            "strategy_class": "elevated_caution",
            "continuity_strength": "medium",
            "trend_direction": "flat",
            "posture": "monitor",
        },
        "pm_review_record": {
            "review_class": "review",
            "review_priority": "medium",
        },
        "pm_planning_record": {
            "plan_class": "prepare_review",
            "next_step_class": "prepare_review",
            "plan_priority": "medium",
        },
        "pm_queue_record": {
            "queue_lane": "review",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "medium",
        },
        "pm_workflow_dispatch_record": {
            "dispatch_class": "review_dispatch",
            "dispatch_target": "pm_review",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
    }


def case_01_system_view_top_level_shape() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)

    _assert(response["status"] == "ok", "status should be ok")
    _assert(response["request_id"] == "live-b3-002", "request_id mismatch")
    _assert("system_view" in response, "system_view missing")

    system_view = response["system_view"]
    expected_keys = {
        "case",
        "runtime",
        "recommendation",
        "cognition",
        "pm_workflow",
        "governance",
    }
    _assert(set(system_view.keys()) == expected_keys, "system_view keys do not match canonical shape")


def case_02_runtime_and_case_projection() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]

    _assert(system_view["case"]["case_id"] == "live-b3-002", "case_id mismatch")
    _assert(system_view["case"]["title"] == "Retail momentum surges on speculative chatter", "case title mismatch")
    _assert(system_view["case"]["input_mode"] == "live", "input_mode should resolve to live")

    _assert(system_view["runtime"]["market_regime"] == "normal", "market_regime mismatch")
    _assert(system_view["runtime"]["event_theme"] == "speculative_move", "event_theme mismatch")
    _assert(system_view["runtime"]["macro_bias"] == "mixed", "macro_bias mismatch")
    _assert(system_view["runtime"]["candidate_count"] == 0, "candidate_count mismatch")


def case_03_recommendation_none_shape_stable() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    recommendation = response["system_view"]["recommendation"]

    _assert(recommendation["state"] == "none", "recommendation state should be none")
    _assert(recommendation["count"] == 0, "recommendation count should be zero")
    _assert(recommendation["items"] == [], "recommendation items should be empty list")
    _assert(isinstance(recommendation["summary"], str), "recommendation summary should be string")


def case_04_refinement_visible_under_cognition() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    refinement = response["system_view"]["cognition"]["refinement"]

    _assert(refinement["state"] == "present", "refinement state should be present")
    _assert(refinement["signal"] == "speculative_signal_detected", "refinement signal mismatch")
    _assert(refinement["confidence_adjustment"] == "down", "confidence adjustment mismatch")
    _assert(refinement["risk_flag"] == "low_confirmation", "risk flag mismatch")
    _assert(refinement["insight"] is not None, "refinement insight should be present")
    _assert(refinement["narrative"] is not None, "refinement narrative should be present")


def case_05_pm_workflow_collapsed_surface() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    workflow = response["system_view"]["pm_workflow"]

    _assert(workflow["state"] == "present", "pm_workflow state should be present")

    strategy = workflow["strategy"]
    review = workflow["review"]
    plan = workflow["plan"]
    queue = workflow["queue"]
    dispatch = workflow["dispatch"]

    _assert(strategy["class"] == "elevated_caution", "strategy class mismatch")
    _assert(strategy["strength"] == "medium", "strategy strength mismatch")
    _assert(strategy["trend"] == "flat", "strategy trend mismatch")
    _assert(strategy["posture"] == "monitor", "strategy posture mismatch")

    _assert(review["class"] == "review", "review class mismatch")
    _assert(review["priority"] == "medium", "review priority mismatch")

    _assert(plan["class"] == "prepare_review", "plan class mismatch")
    _assert(plan["next_step"] == "prepare_review", "plan next_step mismatch")

    _assert(queue["lane"] == "review", "queue lane mismatch")
    _assert(queue["status"] == "queued", "queue status mismatch")
    _assert(queue["target"] == "pm", "queue target mismatch")

    _assert(dispatch["class"] == "review_dispatch", "dispatch class mismatch")
    _assert(dispatch["target"] == "pm_review", "dispatch target mismatch")
    _assert(dispatch["status"] == "ready", "dispatch status mismatch")
    _assert(dispatch["ready"] is True, "dispatch ready mismatch")


def case_06_governance_truth_preserved() -> None:
    payload = _base_payload()
    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    governance = response["system_view"]["governance"]

    _assert(governance["mode"] == "advisory", "governance mode mismatch")
    _assert(governance["route_mode"] == "pm_route_live", "route_mode mismatch")
    _assert(governance["execution_allowed"] is False, "execution_allowed must remain false")
    _assert(governance["approval_required"] is True, "approval_required must remain true")
    _assert(governance["watcher_passed"] is True, "watcher_passed mismatch")
    _assert(governance["closeout_status"] == "accepted", "closeout_status mismatch")
    _assert(governance["requires_review"] is False, "requires_review mismatch")


def case_07_rejected_shape_still_stable() -> None:
    payload = _base_payload()
    payload["rejection_panel"] = {"reason": "speculative move rejected"}
    payload["recommendation_panel"] = {"recommendation_count": 0, "recommendations": []}

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]

    _assert("recommendation" in system_view, "recommendation panel missing")
    _assert("cognition" in system_view, "cognition panel missing")
    _assert("pm_workflow" in system_view, "pm_workflow panel missing")
    _assert(system_view["recommendation"]["state"] == "rejected", "recommendation state should be rejected")
    _assert(system_view["recommendation"]["summary"] == "speculative move rejected", "rejection summary mismatch")


def case_08_zero_pm_records_supported() -> None:
    payload = _base_payload()
    payload.pop("pm_strategy_record", None)
    payload.pop("pm_review_record", None)
    payload.pop("pm_planning_record", None)
    payload.pop("pm_queue_record", None)
    payload.pop("pm_workflow_dispatch_record", None)

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    workflow = response["system_view"]["pm_workflow"]

    _assert(workflow["state"] == "none", "pm_workflow state should be none when no records exist")
    _assert(workflow["dispatch"]["ready"] is False, "dispatch ready should default false")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_system_view_top_level_shape", case_01_system_view_top_level_shape),
    ("case_02_runtime_and_case_projection", case_02_runtime_and_case_projection),
    ("case_03_recommendation_none_shape_stable", case_03_recommendation_none_shape_stable),
    ("case_04_refinement_visible_under_cognition", case_04_refinement_visible_under_cognition),
    ("case_05_pm_workflow_collapsed_surface", case_05_pm_workflow_collapsed_surface),
    ("case_06_governance_truth_preserved", case_06_governance_truth_preserved),
    ("case_07_rejected_shape_still_stable", case_07_rejected_shape_still_stable),
    ("case_08_zero_pm_records_supported", case_08_zero_pm_records_supported),
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

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
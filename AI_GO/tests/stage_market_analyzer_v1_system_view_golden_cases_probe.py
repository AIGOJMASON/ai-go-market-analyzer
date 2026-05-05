from __future__ import annotations

from typing import Any, Callable, Dict, List

from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _base_payload(
    *,
    request_id: str,
    title: str,
    route_mode: str,
    input_mode: str,
    event_theme: str,
    macro_bias: str,
    candidate_symbols: List[str],
    recommendations: List[Dict[str, Any]],
    refinement_panel: Dict[str, Any],
    pm_strategy_record: Dict[str, Any] | None = None,
    pm_review_record: Dict[str, Any] | None = None,
    pm_planning_record: Dict[str, Any] | None = None,
    pm_queue_record: Dict[str, Any] | None = None,
    pm_workflow_dispatch_record: Dict[str, Any] | None = None,
    rejection_reason: str | None = None,
    requires_review: bool = False,
    watcher_passed: bool = True,
    closeout_status: str = "accepted",
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": "ok",
        "request_id": request_id,
        "route_mode": route_mode,
        "input_mode": input_mode,
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "receipt_id": f"rcpt_{request_id}",
        "watcher_validation_id": f"watcher_{request_id}",
        "closeout_id": f"closeout_{request_id}",
        "closeout_status": closeout_status,
        "requires_review": requires_review,
        "governance_panel": {
            "watcher_passed": watcher_passed,
        },
        "case_panel": {
            "case_id": request_id,
            "title": title,
            "observed_at": None,
        },
        "market_panel": {
            "market_regime": "normal",
            "event_theme": event_theme,
            "macro_bias": macro_bias,
            "headline": title,
        },
        "candidate_panel": {
            "candidate_count": len(candidate_symbols),
            "symbols": candidate_symbols,
        },
        "recommendation_panel": {
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
        },
        "refinement_panel": refinement_panel,
    }

    if rejection_reason is not None:
        payload["rejection_panel"] = {"reason": rejection_reason}

    if pm_strategy_record is not None:
        payload["pm_strategy_record"] = pm_strategy_record
    if pm_review_record is not None:
        payload["pm_review_record"] = pm_review_record
    if pm_planning_record is not None:
        payload["pm_planning_record"] = pm_planning_record
    if pm_queue_record is not None:
        payload["pm_queue_record"] = pm_queue_record
    if pm_workflow_dispatch_record is not None:
        payload["pm_workflow_dispatch_record"] = pm_workflow_dispatch_record

    return payload


def case_01_necessity_rebound_positive_flow() -> None:
    payload = _base_payload(
        request_id="golden-001",
        title="Energy rebound after necessity shock",
        route_mode="pm_route_live",
        input_mode="live",
        event_theme="energy_rebound",
        macro_bias="supportive",
        candidate_symbols=["XLE"],
        recommendations=[
            {
                "symbol": "XLE",
                "entry": "reclaim support",
                "exit": "short-term resistance",
                "confidence": "medium",
            }
        ],
        refinement_panel={
            "signal": "necessity_rebound_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Supportive rebound aligned with necessity context.",
            "narrative": "Governed signal remains advisory and non-executing.",
        },
        pm_strategy_record={
            "strategy_class": "reinforced_support",
            "continuity_strength": "medium",
            "trend_direction": "up",
            "posture": "supportive",
        },
        pm_review_record={
            "review_class": "plan",
            "review_priority": "medium",
        },
        pm_planning_record={
            "plan_class": "prepare_plan",
            "next_step_class": "prepare_plan",
            "plan_priority": "medium",
        },
        pm_queue_record={
            "queue_lane": "planning",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "medium",
        },
        pm_workflow_dispatch_record={
            "dispatch_class": "planning_dispatch",
            "dispatch_target": "pm_planning",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
    )

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]

    _assert(system_view["case"]["input_mode"] == "live", "positive flow should resolve to live mode")
    _assert(system_view["recommendation"]["state"] == "present", "positive flow should have recommendation")
    _assert(system_view["recommendation"]["count"] == 1, "positive flow should emit one recommendation")
    _assert(system_view["runtime"]["event_theme"] == "energy_rebound", "event theme mismatch")
    _assert(system_view["cognition"]["refinement"]["signal"] == "necessity_rebound_confirmed", "refinement signal mismatch")
    _assert(system_view["pm_workflow"]["strategy"]["class"] == "reinforced_support", "strategy class mismatch")
    _assert(system_view["pm_workflow"]["dispatch"]["ready"] is True, "dispatch should be ready")
    _assert(system_view["governance"]["execution_allowed"] is False, "execution must remain blocked")


def case_02_speculative_move_rejection_flow() -> None:
    payload = _base_payload(
        request_id="golden-002",
        title="Retail momentum surges on speculative chatter",
        route_mode="pm_route_live",
        input_mode="live",
        event_theme="speculative_move",
        macro_bias="mixed",
        candidate_symbols=[],
        recommendations=[],
        refinement_panel={
            "signal": "speculative_signal_detected",
            "confidence_adjustment": "down",
            "risk_flag": "low_confirmation",
            "insight": "Speculative move lacks necessity support.",
            "narrative": "Signal present, but confidence reduced due to weak confirmation.",
        },
        pm_strategy_record={
            "strategy_class": "elevated_caution",
            "continuity_strength": "medium",
            "trend_direction": "flat",
            "posture": "monitor",
        },
        pm_review_record={
            "review_class": "review",
            "review_priority": "medium",
        },
        pm_planning_record={
            "plan_class": "prepare_review",
            "next_step_class": "prepare_review",
            "plan_priority": "medium",
        },
        pm_queue_record={
            "queue_lane": "review",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "medium",
        },
        pm_workflow_dispatch_record={
            "dispatch_class": "review_dispatch",
            "dispatch_target": "pm_review",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
        rejection_reason="speculative move rejected",
    )

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]

    _assert(system_view["recommendation"]["state"] == "rejected", "speculative move should be rejected")
    _assert(system_view["recommendation"]["count"] == 0, "rejected case should have zero recommendations")
    _assert(system_view["recommendation"]["summary"] == "speculative move rejected", "rejection summary mismatch")
    _assert(system_view["cognition"]["refinement"]["confidence_adjustment"] == "down", "confidence should be adjusted down")
    _assert(system_view["pm_workflow"]["strategy"]["class"] == "elevated_caution", "strategy should reflect caution")
    _assert(system_view["pm_workflow"]["review"]["class"] == "review", "review posture mismatch")


def case_03_missing_confirmation_blocks_recommendation() -> None:
    payload = _base_payload(
        request_id="golden-003",
        title="Energy move without confirmation support",
        route_mode="pm_route_live",
        input_mode="live",
        event_theme="confirmation_failure",
        macro_bias="mixed",
        candidate_symbols=[],
        recommendations=[],
        refinement_panel={
            "signal": "confirmation_missing",
            "confidence_adjustment": "down",
            "risk_flag": "missing_confirmation",
            "insight": "No rebound validation present.",
            "narrative": "Signal remains non-executable without confirmation.",
        },
        pm_strategy_record={
            "strategy_class": "monitor",
            "continuity_strength": "low",
            "trend_direction": "flat",
            "posture": "watch",
        },
        pm_review_record={
            "review_class": "observe",
            "review_priority": "low",
        },
        pm_planning_record={
            "plan_class": "hold_observe",
            "next_step_class": "hold_observe",
            "plan_priority": "low",
        },
        pm_queue_record={
            "queue_lane": "hold",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "low",
        },
        pm_workflow_dispatch_record={
            "dispatch_class": "hold_dispatch",
            "dispatch_target": "pm_hold",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
    )

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]

    _assert(system_view["recommendation"]["state"] == "none", "missing confirmation should not recommend")
    _assert(system_view["recommendation"]["count"] == 0, "missing confirmation should have zero recommendations")
    _assert(system_view["runtime"]["event_theme"] == "confirmation_failure", "event theme mismatch")
    _assert(system_view["cognition"]["refinement"]["risk_flag"] == "missing_confirmation", "risk flag mismatch")
    _assert(system_view["pm_workflow"]["review"]["class"] == "observe", "review class should be observe")
    _assert(system_view["pm_workflow"]["queue"]["lane"] == "hold", "queue lane should be hold")


def case_04_review_required_case_preserves_governance_truth() -> None:
    payload = _base_payload(
        request_id="golden-004",
        title="Watcher accepted but manual review required",
        route_mode="pm_route_live",
        input_mode="live",
        event_theme="energy_rebound",
        macro_bias="supportive",
        candidate_symbols=["XLE"],
        recommendations=[
            {
                "symbol": "XLE",
                "entry": "reclaim support",
                "exit": "short-term resistance",
                "confidence": "medium",
            }
        ],
        refinement_panel={
            "signal": "necessity_rebound_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Supportive rebound aligned with necessity context.",
            "narrative": "Governed signal remains advisory and non-executing.",
        },
        pm_strategy_record={
            "strategy_class": "escalate_for_pm_review",
            "continuity_strength": "high",
            "trend_direction": "up",
            "posture": "escalate",
        },
        pm_review_record={
            "review_class": "escalate",
            "review_priority": "high",
        },
        pm_planning_record={
            "plan_class": "prepare_escalation",
            "next_step_class": "prepare_escalation",
            "plan_priority": "high",
        },
        pm_queue_record={
            "queue_lane": "escalation",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "high",
        },
        pm_workflow_dispatch_record={
            "dispatch_class": "escalation_dispatch",
            "dispatch_target": "pm_escalation",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
        requires_review=True,
        watcher_passed=True,
        closeout_status="accepted",
    )

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    governance = response["system_view"]["governance"]
    workflow = response["system_view"]["pm_workflow"]

    _assert(governance["watcher_passed"] is True, "watcher status mismatch")
    _assert(governance["requires_review"] is True, "requires_review should be true")
    _assert(governance["execution_allowed"] is False, "execution must remain blocked")
    _assert(workflow["strategy"]["class"] == "escalate_for_pm_review", "strategy class mismatch")
    _assert(workflow["review"]["class"] == "escalate", "review class mismatch")
    _assert(workflow["queue"]["lane"] == "escalation", "queue lane mismatch")


def case_05_zero_pm_records_still_returns_stable_shape() -> None:
    payload = _base_payload(
        request_id="golden-005",
        title="Stable runtime with no PM records attached",
        route_mode="pm_route",
        input_mode="fixture",
        event_theme="energy_rebound",
        macro_bias="supportive",
        candidate_symbols=["XLE"],
        recommendations=[
            {
                "symbol": "XLE",
                "entry": "reclaim support",
                "exit": "short-term resistance",
                "confidence": "medium",
            }
        ],
        refinement_panel={
            "signal": "necessity_rebound_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Supportive rebound aligned with necessity context.",
            "narrative": "Governed signal remains advisory and non-executing.",
        },
    )

    response = build_market_analyzer_response(payload).model_dump(by_alias=True)
    system_view = response["system_view"]
    workflow = system_view["pm_workflow"]

    _assert("case" in system_view, "case panel missing")
    _assert("runtime" in system_view, "runtime panel missing")
    _assert("recommendation" in system_view, "recommendation panel missing")
    _assert("cognition" in system_view, "cognition panel missing")
    _assert("pm_workflow" in system_view, "pm_workflow panel missing")
    _assert("governance" in system_view, "governance panel missing")
    _assert(workflow["state"] == "none", "pm_workflow should resolve to none when PM records are absent")
    _assert(workflow["dispatch"]["ready"] is False, "dispatch ready should default false")
    _assert(system_view["case"]["input_mode"] == "fixture", "fixture mode mismatch")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_necessity_rebound_positive_flow", case_01_necessity_rebound_positive_flow),
    ("case_02_speculative_move_rejection_flow", case_02_speculative_move_rejection_flow),
    ("case_03_missing_confirmation_blocks_recommendation", case_03_missing_confirmation_blocks_recommendation),
    ("case_04_review_required_case_preserves_governance_truth", case_04_review_required_case_preserves_governance_truth),
    ("case_05_zero_pm_records_still_returns_stable_shape", case_05_zero_pm_records_still_returns_stable_shape),
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
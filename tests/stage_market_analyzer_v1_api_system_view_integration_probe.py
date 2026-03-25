from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi import FastAPI
from fastapi.testclient import TestClient

from AI_GO.api.market_analyzer_api import router


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def _patch_runtime_stub() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    import AI_GO.api.market_analyzer_api as market_analyzer_api

    original = market_analyzer_api._run_market_analyzer_logic

    def stub(request_payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = request_payload.get("request_id", "test-001")
        headline = request_payload.get("headline", "Energy rebound after necessity shock")
        symbol = request_payload.get("symbol", "XLE")

        is_live = "price_change_pct" in request_payload or "sector" in request_payload or "confirmation" in request_payload
        route_mode = "pm_route_live" if is_live else "pm_route"
        input_mode = "live" if is_live else "fixture"

        if request_payload.get("force_rejection") is True:
            return {
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
                "closeout_status": "accepted",
                "requires_review": False,
                "governance_panel": {
                    "watcher_passed": True,
                },
                "case_panel": {
                    "case_id": request_id,
                    "title": headline,
                    "observed_at": None,
                },
                "market_panel": {
                    "market_regime": "normal",
                    "event_theme": "speculative_move",
                    "macro_bias": "mixed",
                    "headline": headline,
                },
                "candidate_panel": {
                    "candidate_count": 0,
                    "symbols": [],
                },
                "recommendation_panel": {
                    "recommendation_count": 0,
                    "recommendations": [],
                },
                "rejection_panel": {
                    "reason": "speculative move rejected",
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

        return {
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
            "closeout_status": "accepted",
            "requires_review": False,
            "governance_panel": {
                "watcher_passed": True,
            },
            "case_panel": {
                "case_id": request_id,
                "title": headline,
                "observed_at": None,
            },
            "market_panel": {
                "market_regime": "normal",
                "event_theme": "energy_rebound",
                "macro_bias": "supportive",
                "headline": headline,
            },
            "candidate_panel": {
                "candidate_count": 1,
                "symbols": [symbol],
            },
            "recommendation_panel": {
                "recommendation_count": 1,
                "recommendations": [
                    {
                        "symbol": symbol,
                        "entry": "reclaim support",
                        "exit": "short-term resistance",
                        "confidence": "medium",
                    }
                ],
            },
            "refinement_panel": {
                "signal": "necessity_rebound_confirmed",
                "confidence_adjustment": "none",
                "risk_flag": None,
                "insight": "Supportive rebound aligned with necessity context.",
                "narrative": "Governed signal remains advisory and non-executing.",
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

    market_analyzer_api._run_market_analyzer_logic = stub

    def restore(original_fn: Callable[[Dict[str, Any]], Dict[str, Any]] = original) -> None:
        market_analyzer_api._run_market_analyzer_logic = original_fn

    return restore


def case_01_run_endpoint_returns_system_view_shape() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run",
            json={
                "request_id": "run-001",
                "case_id": "fixture-energy-001",
            },
        )

        _assert(response.status_code == 200, "run endpoint should return 200")
        body = response.json()

        _assert(body["status"] == "ok", "status should be ok")
        _assert(body["request_id"] == "run-001", "request_id mismatch")
        _assert("system_view" in body, "system_view missing")

        system_view = body["system_view"]
        expected_keys = {
            "case",
            "runtime",
            "recommendation",
            "cognition",
            "pm_workflow",
            "governance",
        }
        _assert(set(system_view.keys()) == expected_keys, "system_view keys do not match canonical shape")
    finally:
        restore()


def case_02_run_endpoint_fixture_mode_and_recommendation_projection() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run",
            json={
                "request_id": "run-002",
                "case_id": "fixture-energy-002",
            },
        )

        _assert(response.status_code == 200, "run endpoint should return 200")
        body = response.json()
        system_view = body["system_view"]

        _assert(system_view["case"]["input_mode"] == "fixture", "input_mode should resolve to fixture")
        _assert(system_view["runtime"]["event_theme"] == "energy_rebound", "event_theme mismatch")
        _assert(system_view["recommendation"]["state"] == "present", "recommendation state should be present")
        _assert(system_view["recommendation"]["count"] == 1, "recommendation count should be one")
        _assert(system_view["recommendation"]["items"][0]["symbol"] == "XLE", "recommendation symbol mismatch")
    finally:
        restore()


def case_03_live_endpoint_returns_live_system_view() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "live-001",
                "symbol": "XLE",
                "headline": "Energy rebound after necessity shock",
                "price_change_pct": 3.2,
                "sector": "energy",
                "confirmation": "partial",
            },
        )

        _assert(response.status_code == 200, "live endpoint should return 200")
        body = response.json()
        system_view = body["system_view"]

        _assert(system_view["case"]["input_mode"] == "live", "input_mode should resolve to live")
        _assert(system_view["runtime"]["candidate_count"] == 1, "candidate_count mismatch")
        _assert(system_view["runtime"]["candidates"] == ["XLE"], "candidate symbols mismatch")
        _assert(system_view["governance"]["route_mode"] == "pm_route_live", "route_mode should reflect live flow")
    finally:
        restore()


def case_04_cognition_and_pm_workflow_present_end_to_end() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "live-002",
                "symbol": "XLE",
                "headline": "Energy rebound after necessity shock",
                "price_change_pct": 2.8,
                "sector": "energy",
                "confirmation": "confirmed",
            },
        )

        _assert(response.status_code == 200, "live endpoint should return 200")
        body = response.json()
        refinement = body["system_view"]["cognition"]["refinement"]
        workflow = body["system_view"]["pm_workflow"]

        _assert(refinement["state"] == "present", "refinement state should be present")
        _assert(refinement["signal"] == "necessity_rebound_confirmed", "refinement signal mismatch")
        _assert(workflow["state"] == "present", "pm_workflow state should be present")
        _assert(workflow["strategy"]["class"] == "reinforced_support", "strategy class mismatch")
        _assert(workflow["review"]["class"] == "plan", "review class mismatch")
        _assert(workflow["plan"]["class"] == "prepare_plan", "plan class mismatch")
        _assert(workflow["queue"]["lane"] == "planning", "queue lane mismatch")
        _assert(workflow["dispatch"]["class"] == "planning_dispatch", "dispatch class mismatch")
        _assert(workflow["dispatch"]["ready"] is True, "dispatch ready mismatch")
    finally:
        restore()


def case_05_governance_invariants_preserved_end_to_end() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "live-003",
                "symbol": "XLE",
                "headline": "Energy rebound after necessity shock",
                "price_change_pct": 4.1,
                "sector": "energy",
                "confirmation": "confirmed",
            },
        )

        _assert(response.status_code == 200, "live endpoint should return 200")
        governance = response.json()["system_view"]["governance"]

        _assert(governance["mode"] == "advisory", "mode should remain advisory")
        _assert(governance["execution_allowed"] is False, "execution_allowed must remain false")
        _assert(governance["approval_required"] is True, "approval_required must remain true")
        _assert(governance["watcher_passed"] is True, "watcher_passed mismatch")
        _assert(governance["closeout_status"] == "accepted", "closeout_status mismatch")
    finally:
        restore()


def case_06_rejected_case_keeps_same_shape_end_to_end() -> None:
    restore = _patch_runtime_stub()
    try:
        app = _build_test_app()
        client = TestClient(app)

        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "live-004",
                "symbol": "XRT",
                "headline": "Retail momentum surges on speculative chatter",
                "price_change_pct": 3.5,
                "sector": "retail",
                "confirmation": "partial",
                "force_rejection": True,
            },
        )

        _assert(response.status_code == 200, "live endpoint should return 200")
        body = response.json()
        system_view = body["system_view"]

        _assert("recommendation" in system_view, "recommendation panel missing")
        _assert("cognition" in system_view, "cognition panel missing")
        _assert("pm_workflow" in system_view, "pm_workflow panel missing")
        _assert(system_view["recommendation"]["state"] == "rejected", "recommendation state should be rejected")
        _assert(system_view["recommendation"]["summary"] == "speculative move rejected", "rejection summary mismatch")
    finally:
        restore()


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_run_endpoint_returns_system_view_shape", case_01_run_endpoint_returns_system_view_shape),
    ("case_02_run_endpoint_fixture_mode_and_recommendation_projection", case_02_run_endpoint_fixture_mode_and_recommendation_projection),
    ("case_03_live_endpoint_returns_live_system_view", case_03_live_endpoint_returns_live_system_view),
    ("case_04_cognition_and_pm_workflow_present_end_to_end", case_04_cognition_and_pm_workflow_present_end_to_end),
    ("case_05_governance_invariants_preserved_end_to_end", case_05_governance_invariants_preserved_end_to_end),
    ("case_06_rejected_case_keeps_same_shape_end_to_end", case_06_rejected_case_keeps_same_shape_end_to_end),
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
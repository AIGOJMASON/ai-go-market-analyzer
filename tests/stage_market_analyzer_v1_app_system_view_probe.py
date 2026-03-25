from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi.testclient import TestClient

from AI_GO.app import app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _patch_runtime_stub() -> Callable[[], None]:
    import AI_GO.api.market_analyzer_api as market_analyzer_api

    original = market_analyzer_api._run_market_analyzer_logic

    def stub(request_payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = request_payload.get("request_id", "test-001")
        headline = request_payload.get("headline", "Energy rebound after necessity shock")
        symbol = request_payload.get("symbol", "XLE")

        is_live = any(
            key in request_payload
            for key in ["price_change_pct", "sector", "confirmation"]
        )
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

    def restore() -> None:
        market_analyzer_api._run_market_analyzer_logic = original

    return restore


def case_01_root_or_health_surface_available() -> None:
    client = TestClient(app)

    root_response = client.get("/")
    health_response = client.get("/healthz")

    _assert(
        root_response.status_code == 200 or health_response.status_code == 200,
        "expected root or healthz to be available on mounted app",
    )


def case_02_root_surface_is_reachable() -> None:
    client = TestClient(app)
    response = client.get("/")

    _assert(response.status_code == 200, "mounted root route should be reachable")
    _assert(isinstance(response.text, str), "root response should be text/html compatible")
    _assert(len(response.text) > 0, "root response should not be empty")


def case_03_run_route_returns_system_view_from_real_app() -> None:
    restore = _patch_runtime_stub()
    try:
        client = TestClient(app)
        response = client.post(
            "/market-analyzer/run",
            json={
                "request_id": "app-run-001",
                "case_id": "fixture-energy-001",
            },
        )

        _assert(response.status_code == 200, "run route should return 200")
        body = response.json()

        _assert(body["status"] == "ok", "status should be ok")
        _assert("system_view" in body, "system_view missing")
        _assert(body["system_view"]["case"]["input_mode"] == "fixture", "fixture mode mismatch")
        _assert(body["system_view"]["recommendation"]["state"] == "present", "recommendation should be present")
    finally:
        restore()


def case_04_live_route_returns_live_system_view_from_real_app() -> None:
    restore = _patch_runtime_stub()
    try:
        client = TestClient(app)
        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "app-live-001",
                "symbol": "XLE",
                "headline": "Energy rebound after necessity shock",
                "price_change_pct": 3.2,
                "sector": "energy",
                "confirmation": "partial",
            },
        )

        _assert(response.status_code == 200, "live route should return 200")
        body = response.json()
        system_view = body["system_view"]

        _assert(system_view["case"]["input_mode"] == "live", "live mode mismatch")
        _assert(system_view["runtime"]["event_theme"] == "energy_rebound", "event theme mismatch")
        _assert(system_view["runtime"]["candidates"] == ["XLE"], "candidate projection mismatch")
        _assert(system_view["governance"]["route_mode"] == "pm_route_live", "route mode mismatch")
    finally:
        restore()


def case_05_real_app_preserves_cognition_pm_workflow_and_governance() -> None:
    restore = _patch_runtime_stub()
    try:
        client = TestClient(app)
        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "app-live-002",
                "symbol": "XLE",
                "headline": "Energy rebound after necessity shock",
                "price_change_pct": 2.7,
                "sector": "energy",
                "confirmation": "confirmed",
            },
        )

        _assert(response.status_code == 200, "live route should return 200")
        body = response.json()
        refinement = body["system_view"]["cognition"]["refinement"]
        workflow = body["system_view"]["pm_workflow"]
        governance = body["system_view"]["governance"]

        _assert(refinement["state"] == "present", "refinement state mismatch")
        _assert(refinement["signal"] == "necessity_rebound_confirmed", "refinement signal mismatch")

        _assert(workflow["state"] == "present", "pm_workflow state mismatch")
        _assert(workflow["strategy"]["class"] == "reinforced_support", "strategy class mismatch")
        _assert(workflow["dispatch"]["ready"] is True, "dispatch ready mismatch")

        _assert(governance["mode"] == "advisory", "governance mode mismatch")
        _assert(governance["execution_allowed"] is False, "execution should remain blocked")
        _assert(governance["approval_required"] is True, "approval requirement mismatch")
        _assert(governance["watcher_passed"] is True, "watcher_passed mismatch")
    finally:
        restore()


def case_06_real_app_rejected_case_keeps_unified_shape() -> None:
    restore = _patch_runtime_stub()
    try:
        client = TestClient(app)
        response = client.post(
            "/market-analyzer/run/live",
            json={
                "request_id": "app-live-003",
                "symbol": "XRT",
                "headline": "Retail momentum surges on speculative chatter",
                "price_change_pct": 3.5,
                "sector": "retail",
                "confirmation": "partial",
                "force_rejection": True,
            },
        )

        _assert(response.status_code == 200, "live route should return 200")
        body = response.json()
        system_view = body["system_view"]

        _assert("recommendation" in system_view, "recommendation section missing")
        _assert("cognition" in system_view, "cognition section missing")
        _assert("pm_workflow" in system_view, "pm_workflow section missing")
        _assert(system_view["recommendation"]["state"] == "rejected", "recommendation should be rejected")
        _assert(system_view["recommendation"]["summary"] == "speculative move rejected", "rejection summary mismatch")
    finally:
        restore()


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_root_or_health_surface_available", case_01_root_or_health_surface_available),
    ("case_02_root_surface_is_reachable", case_02_root_surface_is_reachable),
    ("case_03_run_route_returns_system_view_from_real_app", case_03_run_route_returns_system_view_from_real_app),
    ("case_04_live_route_returns_live_system_view_from_real_app", case_04_live_route_returns_live_system_view_from_real_app),
    ("case_05_real_app_preserves_cognition_pm_workflow_and_governance", case_05_real_app_preserves_cognition_pm_workflow_and_governance),
    ("case_06_real_app_rejected_case_keeps_unified_shape", case_06_real_app_rejected_case_keeps_unified_shape),
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
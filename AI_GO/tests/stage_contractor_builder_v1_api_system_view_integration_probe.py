from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi import FastAPI
from fastapi.testclient import TestClient

from AI_GO.child_cores.contractor_builder_v1.api.contractor_builder_api import router


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def case_01_run_route_returns_system_view() -> None:
    client = TestClient(_build_test_app())
    response = client.post("/contractor-builder/run", json={"request_id": "fixture-001", "case_id": "fixture-case-001"})

    _assert(response.status_code == 200, "run route should return 200")
    body = response.json()
    _assert("system_view" in body, "system_view missing")
    _assert(body["system_view"]["case"]["input_mode"] == "fixture", "fixture input_mode mismatch")


def case_02_live_route_returns_live_system_view() -> None:
    client = TestClient(_build_test_app())
    response = client.post(
        "/contractor-builder/run/live",
        json={
            "request_id": "live-001",
            "project_type": "remodel",
            "trade_focus": "interior",
            "scope_summary": "Interior kitchen refresh",
            "budget_band": "medium",
            "timeline_band": "near_term",
            "location_mode": "remote",
            "confirmation": "partial"
        },
    )

    _assert(response.status_code == 200, "live route should return 200")
    body = response.json()
    _assert(body["system_view"]["case"]["input_mode"] == "live", "live input_mode mismatch")
    _assert(body["system_view"]["recommendation"]["state"] == "present", "recommendation should be present")


def case_03_rejected_live_route_keeps_shape() -> None:
    client = TestClient(_build_test_app())
    response = client.post(
        "/contractor-builder/run/live",
        json={
            "request_id": "live-002",
            "project_type": "repair",
            "trade_focus": "electrical",
            "scope_summary": "Panel review only",
            "budget_band": "low",
            "timeline_band": "urgent",
            "location_mode": "onsite",
            "confirmation": "missing"
        },
    )

    _assert(response.status_code == 200, "rejected live route should return 200")
    body = response.json()
    _assert(body["system_view"]["recommendation"]["state"] in {"none", "rejected"}, "rejected route shape mismatch")
    _assert("pm_workflow" in body["system_view"], "pm_workflow missing")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_run_route_returns_system_view", case_01_run_route_returns_system_view),
    ("case_02_live_route_returns_live_system_view", case_02_live_route_returns_live_system_view),
    ("case_03_rejected_live_route_keeps_shape", case_03_rejected_live_route_keeps_shape),
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
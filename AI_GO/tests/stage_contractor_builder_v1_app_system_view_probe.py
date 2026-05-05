from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi.testclient import TestClient

from AI_GO.child_cores.contractor_builder_v1.app import app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_root_advertises_operator() -> None:
    client = TestClient(app)
    response = client.get("/")

    _assert(response.status_code == 200, "root should return 200")
    body = response.json()
    _assert(body["operator_route"] == "/operator", "root should advertise /operator")


def case_02_operator_route_loads() -> None:
    client = TestClient(app)
    response = client.get("/operator")
    _assert(response.status_code == 200, "/operator should return 200")
    _assert("AI_GO Contractor Builder V1" in response.text, "operator title missing")


def case_03_live_route_works_through_app() -> None:
    client = TestClient(app)
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
    _assert(response.status_code == 200, "live route should return 200 through app")
    _assert("system_view" in response.json(), "system_view missing through app")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_root_advertises_operator", case_01_root_advertises_operator),
    ("case_02_operator_route_loads", case_02_operator_route_loads),
    ("case_03_live_route_works_through_app", case_03_live_route_works_through_app),
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
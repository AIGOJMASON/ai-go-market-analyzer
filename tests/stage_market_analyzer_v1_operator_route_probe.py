from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi.testclient import TestClient

from AI_GO.app import app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_operator_route_loads() -> None:
    client = TestClient(app)
    response = client.get("/operator")

    _assert(response.status_code == 200, "/operator should return 200")
    _assert("AI_GO Operator Dashboard" in response.text, "operator title missing")


def case_02_operator_route_has_unified_sections() -> None:
    client = TestClient(app)
    html = client.get("/operator").text

    for section in [
        "Operator System View",
        "Case",
        "Runtime",
        "Recommendation",
        "Cognition",
        "PM Workflow",
        "Governance",
    ]:
        _assert(section in html, f"missing operator section: {section}")


def case_03_operator_route_uses_live_api_surface() -> None:
    client = TestClient(app)
    html = client.get("/operator").text
    _assert("/market-analyzer/run/live" in html, "operator route should reference live API endpoint")


def case_04_root_points_to_operator_route() -> None:
    client = TestClient(app)
    body = client.get("/").json()

    _assert("routes" in body, "root should expose routes object")
    _assert(body["routes"]["operator"] == "/operator", "root should advertise /operator under routes.operator")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_operator_route_loads", case_01_operator_route_loads),
    ("case_02_operator_route_has_unified_sections", case_02_operator_route_has_unified_sections),
    ("case_03_operator_route_uses_live_api_surface", case_03_operator_route_uses_live_api_surface),
    ("case_04_root_points_to_operator_route", case_04_root_points_to_operator_route),
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
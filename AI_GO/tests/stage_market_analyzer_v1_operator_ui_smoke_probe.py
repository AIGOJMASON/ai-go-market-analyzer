from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi.testclient import TestClient

from AI_GO.app import app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_01_operator_page_loads() -> None:
    client = TestClient(app)
    response = client.get("/operator")

    _assert(response.status_code == 200, "/operator should return 200")
    _assert("AI_GO Operator Dashboard" in response.text, "operator page title missing")


def case_02_operator_page_has_expected_sections() -> None:
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
        _assert(section in html, f"missing section heading: {section}")


def case_03_operator_page_references_live_route() -> None:
    client = TestClient(app)
    html = client.get("/operator").text

    _assert("/market-analyzer/run/live" in html, "operator page should reference live API route")


def case_04_operator_page_has_expected_controls() -> None:
    client = TestClient(app)
    html = client.get("/operator").text

    for control in [
        'id="request_id"',
        'id="symbol"',
        'id="headline"',
        'id="price_change_pct"',
        'id="sector"',
        'id="confirmation"',
        'id="run_live_btn"',
    ]:
        _assert(control in html, f"missing operator control: {control}")


TEST_CASES: List[tuple[str, Callable[[], None]]] = [
    ("case_01_operator_page_loads", case_01_operator_page_loads),
    ("case_02_operator_page_has_expected_sections", case_02_operator_page_has_expected_sections),
    ("case_03_operator_page_references_live_route", case_03_operator_page_references_live_route),
    ("case_04_operator_page_has_expected_controls", case_04_operator_page_has_expected_controls),
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
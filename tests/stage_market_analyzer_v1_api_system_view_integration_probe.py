from __future__ import annotations

import os
from typing import Any, Callable, Dict, List

from fastapi.testclient import TestClient

# Test env must be set before app import
os.environ.setdefault("AI_GO_API_KEYS_JSON", '{"local_operator":"change-me-local"}')
os.environ.setdefault("AI_GO_API_KEY_HEADER", "x-api-key")
os.environ.setdefault("AI_GO_RATE_LIMIT_REQUESTS", "100")
os.environ.setdefault("AI_GO_RATE_LIMIT_WINDOW_SECONDS", "60")
os.environ.setdefault("AI_GO_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver")

from AI_GO.app import app  # noqa: E402


API_HEADERS = {"x-api-key": "change-me-local"}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _client() -> TestClient:
    return TestClient(app)


def case_01_run_endpoint_returns_system_view_shape() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run",
        headers=API_HEADERS,
        json={
            "request_id": "fixture-001",
            "case_id": "fixture-case-001",
        },
    )

    _assert(response.status_code == 200, "run endpoint should return 200")
    body = response.json()
    _assert("system_view" in body, "system_view missing")
    expected_sections = {"case", "runtime", "recommendation", "cognition", "pm_workflow", "governance"}
    _assert(set(body["system_view"].keys()) == expected_sections, "system_view top-level shape mismatch")


def case_02_run_endpoint_fixture_mode_and_recommendation_projection() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run",
        headers=API_HEADERS,
        json={
            "request_id": "fixture-002",
            "case_id": "fixture-case-002",
        },
    )

    _assert(response.status_code == 200, "run endpoint should return 200")
    body = response.json()
    _assert(body["system_view"]["case"]["input_mode"] == "fixture", "fixture input_mode mismatch")
    _assert("recommendation" in body["system_view"], "recommendation section missing")


def case_03_live_endpoint_returns_live_system_view() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run/live",
        headers=API_HEADERS,
        json={
            "request_id": "live-001",
            "symbol": "XLE",
            "headline": "Energy rebound after necessity shock",
            "price_change_pct": 2.4,
            "sector": "energy",
            "confirmation": "confirmed",
        },
    )

    _assert(response.status_code == 200, "live endpoint should return 200")
    body = response.json()
    _assert("system_view" in body, "system_view missing")
    _assert(body["system_view"]["case"]["input_mode"] == "live", "live input_mode mismatch")


def case_04_cognition_and_pm_workflow_present_end_to_end() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run/live",
        headers=API_HEADERS,
        json={
            "request_id": "live-002",
            "symbol": "XLE",
            "headline": "Energy rebound after necessity shock",
            "price_change_pct": 2.4,
            "sector": "energy",
            "confirmation": "confirmed",
        },
    )

    _assert(response.status_code == 200, "live endpoint should return 200")
    body = response.json()
    system_view = body["system_view"]

    _assert("cognition" in system_view, "cognition section missing")
    _assert("pm_workflow" in system_view, "pm_workflow section missing")


def case_05_governance_invariants_preserved_end_to_end() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run/live",
        headers=API_HEADERS,
        json={
            "request_id": "live-003",
            "symbol": "XLE",
            "headline": "Energy rebound after necessity shock",
            "price_change_pct": 2.4,
            "sector": "energy",
            "confirmation": "confirmed",
        },
    )

    _assert(response.status_code == 200, "live endpoint should return 200")
    body = response.json()
    governance = body["system_view"]["governance"]

    _assert(governance["mode"] == "advisory", "mode should remain advisory")
    _assert(governance["execution_allowed"] is False, "execution should remain blocked")


def case_06_rejected_case_keeps_same_shape_end_to_end() -> None:
    client = _client()
    response = client.post(
        "/market-analyzer/run/live",
        headers=API_HEADERS,
        json={
            "request_id": "live-004",
            "symbol": "XLY",
            "headline": "Retail momentum surges on speculative chatter",
            "price_change_pct": 3.5,
            "sector": "industrials",
            "confirmation": "missing",
        },
    )

    _assert(response.status_code == 200, "live endpoint should return 200")
    body = response.json()
    expected_sections = {"case", "runtime", "recommendation", "cognition", "pm_workflow", "governance"}
    _assert(set(body["system_view"].keys()) == expected_sections, "rejected case should keep stable shape")
    _assert(
        body["system_view"]["recommendation"]["state"] in {"none", "rejected", "present"},
        "recommendation state should remain structurally valid",
    )


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

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())
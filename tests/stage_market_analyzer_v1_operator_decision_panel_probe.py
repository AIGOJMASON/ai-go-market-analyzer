from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app


def run_probe() -> dict:
    client = TestClient(app)
    response = client.get("/operator")
    body = response.text

    checks = [
        (
            "case_01_operator_route_loads",
            response.status_code == 200,
        ),
        (
            "case_02_contains_signal_panel",
            "SIGNAL" in body,
        ),
        (
            "case_03_contains_why_it_matters_panel",
            "WHY IT MATTERS" in body,
        ),
        (
            "case_04_contains_recommendation_panel",
            "RECOMMENDATION" in body,
        ),
        (
            "case_05_contains_risk_panel",
            "RISK" in body,
        ),
        (
            "case_06_contains_status_panel",
            "STATUS" in body,
        ),
        (
            "case_07_references_live_run_route",
            "/market-analyzer/run/live" in body,
        ),
        (
            "case_08_mentions_governed_output",
            "governed" in body.lower(),
        ),
    ]

    results = []
    passed = 0
    failed = 0

    for case_name, ok in checks:
        status = "passed" if ok else "failed"
        results.append({"case": case_name, "status": status})
        if ok:
            passed += 1
        else:
            failed += 1

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run_probe())
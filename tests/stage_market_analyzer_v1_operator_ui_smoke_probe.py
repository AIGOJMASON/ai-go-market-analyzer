from __future__ import annotations

from fastapi.testclient import TestClient

from app import app


def run_probe():
    client = TestClient(app)

    response = client.get("/market-analyzer/dashboard")
    body = response.text

    results = [
        {
            "case": "case_01_dashboard_route_returns_200",
            "status": "passed" if response.status_code == 200 else "failed",
        },
        {
            "case": "case_02_dashboard_contains_title",
            "status": "passed" if "AI_GO Market Analyzer V1" in body else "failed",
        },
        {
            "case": "case_03_dashboard_contains_run_button",
            "status": "passed" if "Run Market Analyzer" in body else "failed",
        },
        {
            "case": "case_04_dashboard_calls_market_analyzer_run_endpoint",
            "status": "passed" if "/market-analyzer/run" in body else "failed",
        },
        {
            "case": "case_05_dashboard_contains_refinement_section",
            "status": "passed" if "Refinement Insight" in body else "failed",
        },
    ]

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
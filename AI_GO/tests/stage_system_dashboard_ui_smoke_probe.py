from __future__ import annotations

from fastapi.testclient import TestClient

from app import app


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    client = TestClient(app)

    dashboard_response = client.get("/system-dashboard")
    _assert(dashboard_response.status_code == 200, "system dashboard route did not return 200")
    _assert("AI_GO System Dashboard" in dashboard_response.text, "dashboard title missing")
    _assert("/system/summary" in dashboard_response.text, "dashboard missing system summary fetch path")
    _assert("/system/state" in dashboard_response.text, "dashboard missing system state fetch path")

    summary_response = client.get("/system/summary")
    _assert(summary_response.status_code == 200, "system summary route did not return 200")
    summary_payload = summary_response.json()
    _assert("latest_cycle_id" in summary_payload, "system summary missing latest_cycle_id")
    _assert("eyes_generated_at" in summary_payload, "system summary missing eyes_generated_at")

    state_response = client.get("/system/state")
    _assert(state_response.status_code == 200, "system state route did not return 200")
    state_payload = state_response.json()
    _assert("artifacts" in state_payload, "system state missing artifacts block")
    _assert("system_eyes_packet" in state_payload["artifacts"], "system state missing Eyes artifact")
    _assert("system_cycle_status" in state_payload["artifacts"], "system state missing cycle artifact")

    print(
        {
            "passed": 6,
            "failed": 0,
            "results": [
                {"case": "case_01_dashboard_route_loads", "status": "passed"},
                {"case": "case_02_dashboard_title_present", "status": "passed"},
                {"case": "case_03_summary_route_loads", "status": "passed"},
                {"case": "case_04_summary_has_cycle_fields", "status": "passed"},
                {"case": "case_05_state_route_loads", "status": "passed"},
                {"case": "case_06_state_has_artifact_blocks", "status": "passed"},
            ],
        }
    )


if __name__ == "__main__":
    main()
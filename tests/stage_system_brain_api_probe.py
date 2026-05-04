from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app


def run_probe() -> dict:
    client = TestClient(app)

    response = client.get("/contractor-builder/system-brain/surface?limit=500")
    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    surface = payload["surface"]

    assert surface["artifact_type"] == "operator_system_brain_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True

    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_mutate_state"] is False
    assert surface["authority"]["can_override_governance"] is False
    assert surface["authority"]["can_override_watcher"] is False
    assert surface["authority"]["can_override_execution_gate"] is False

    summary_response = client.get("/contractor-builder/system-brain/summary?limit=500")
    assert summary_response.status_code == 200

    summary_payload = summary_response.json()

    assert summary_payload["status"] == "ok"
    assert summary_payload["mode"] == "read_only"
    assert summary_payload["execution_allowed"] is False
    assert summary_payload["mutation_allowed"] is False
    assert isinstance(summary_payload["plain_summary"], str)

    return {
        "status": "passed",
        "phase": "Phase 4.10",
        "layer": "system_brain_api_surface",
        "surface_route": "/contractor-builder/system-brain/surface",
        "summary_route": "/contractor-builder/system-brain/summary",
        "card_count": len(surface.get("operator_cards", [])),
        "watch_count": len(surface.get("what_to_watch", [])),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_SYSTEM_BRAIN_API_PROBE: PASS")
    print(result)
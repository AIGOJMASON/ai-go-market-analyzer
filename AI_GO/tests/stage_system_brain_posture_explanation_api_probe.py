from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app


def run_probe() -> dict:
    client = TestClient(app)

    response = client.get("/contractor-builder/system-brain/posture-explanation?limit=500")
    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    explanation = payload["posture_explanation"]

    assert explanation["artifact_type"] == "posture_explanation_packet"
    assert explanation["mode"] == "deterministic_read_only_explanation"
    assert explanation["sealed"] is True

    assert explanation["authority"]["read_only"] is True
    assert explanation["authority"]["advisory_only"] is True
    assert explanation["authority"]["ai_generated"] is False
    assert explanation["authority"]["can_execute"] is False
    assert explanation["authority"]["can_mutate_state"] is False
    assert explanation["authority"]["can_override_governance"] is False
    assert explanation["authority"]["can_override_watcher"] is False
    assert explanation["authority"]["can_override_execution_gate"] is False

    assert isinstance(payload["plain_explanation"], str)
    assert len(payload["plain_explanation"]) > 0
    assert isinstance(payload["reasons"], list)

    return {
        "status": "passed",
        "phase": "Phase 4.11.1",
        "layer": "system_brain_posture_explanation_api",
        "route": "/contractor-builder/system-brain/posture-explanation",
        "reason_count": len(payload["reasons"]),
        "plain_explanation": payload["plain_explanation"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_SYSTEM_BRAIN_POSTURE_EXPLANATION_API_PROBE: PASS")
    print(result)
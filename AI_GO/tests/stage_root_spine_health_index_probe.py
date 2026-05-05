from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.root_spine_health import build_root_spine_health_packet


def run_probe() -> dict:
    direct_packet = build_root_spine_health_packet(app=app)

    assert direct_packet["artifact_type"] == "root_spine_health_packet"
    assert direct_packet["phase"] == "Phase 5A.5"
    assert direct_packet["mode"] == "read_only"
    assert direct_packet["authority"]["read_only"] is True
    assert direct_packet["authority"]["can_execute"] is False
    assert direct_packet["authority"]["can_mutate_state"] is False
    assert direct_packet["authority"]["can_fetch_provider"] is False

    direct_summary = direct_packet["summary"]
    assert direct_summary["research_core_active"] is True
    assert direct_summary["engines_active"] is True
    assert direct_summary["smi_active"] is True
    assert direct_summary["market_analyzer_curated_live_present"] is True
    assert direct_summary["contractor_curated_external_pressure_present"] is True

    client = TestClient(app)

    health_response = client.get("/contractor-builder/root-spine/health")
    if health_response.status_code != 200:
        raise AssertionError(
            {
                "expected_status": 200,
                "actual_status": health_response.status_code,
                "response": health_response.json(),
            }
        )

    health_payload = health_response.json()
    assert health_payload["artifact_type"] == "root_spine_health_packet"
    assert health_payload["phase"] == "Phase 5A.5"
    assert health_payload["authority"]["can_execute"] is False

    index_response = client.get("/contractor-builder/root-spine/index")
    if index_response.status_code != 200:
        raise AssertionError(
            {
                "expected_status": 200,
                "actual_status": index_response.status_code,
                "response": index_response.json(),
            }
        )

    index_payload = index_response.json()
    assert index_payload["status"] == "ok"
    assert index_payload["phase"] == "Phase 5A.5"
    assert index_payload["execution_allowed"] is False
    assert index_payload["mutation_allowed"] is False

    route_index = index_payload["route_index"]
    assert route_index["routes"]["market_analyzer_curated_live"]["present"] is True
    assert route_index["routes"]["contractor_curated_external_pressure"]["present"] is True
    assert route_index["routes"]["contractor_root_spine_health"]["present"] is True
    assert route_index["routes"]["contractor_root_spine_index"]["present"] is True

    contractor_health = client.get("/contractor-builder/health")
    assert contractor_health.status_code == 200
    contractor_payload = contractor_health.json()
    assert contractor_payload["routes"]["root_spine"] is True

    return {
        "status": "passed",
        "phase": "Phase 5A.5",
        "health_route": "/contractor-builder/root-spine/health",
        "index_route": "/contractor-builder/root-spine/index",
        "research_core_active": health_payload["summary"]["research_core_active"],
        "engines_active": health_payload["summary"]["engines_active"],
        "smi_active": health_payload["summary"]["smi_active"],
        "market_analyzer_curated_live_present": health_payload["summary"][
            "market_analyzer_curated_live_present"
        ],
        "contractor_curated_external_pressure_present": health_payload["summary"][
            "contractor_curated_external_pressure_present"
        ],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_ROOT_SPINE_HEALTH_INDEX_PROBE: PASS")
    print(result)
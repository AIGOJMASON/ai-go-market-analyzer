from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


def _build_engine_handoff() -> dict:
    research_packet = build_live_research_packet(
        {
            "provider": "marketaux",
            "provider_kind": "market_event_news",
            "source_type": "newswire",
            "signal_type": "contractor_external_pressure",
            "title": "Copper supply pressure may affect job materials",
            "summary": "Curated external signal indicates possible material pricing or timing pressure.",
            "symbol": "COPPER",
            "symbols": ["COPPER"],
            "price": None,
            "price_change_pct": 2.4,
            "sector": "materials",
            "confirmation": "partial",
            "provider_payload": {
                "provider": "marketaux",
                "redacted_for_child_core": True,
            },
            "source_material": [
                {
                    "type": "provider_news_item",
                    "provider": "marketaux",
                    "title": "Copper supply pressure may affect job materials",
                }
            ],
            "source_refs": ["marketaux:item:demo"],
            "child_core_targets": ["contractor_builder_v1"],
        }
    )

    return curate_research_packet_for_child_cores(research_packet)


def run_probe() -> dict:
    client = TestClient(app)

    raw_response = client.post(
        "/contractor-builder/external-pressure/curated",
        json={
            "request_id": "phase-5a4-raw-reject",
            "title": "Raw external pressure should be rejected",
            "summary": "This should not be accepted because it is not engine-curated.",
            "symbol": "COPPER",
        },
    )

    if raw_response.status_code != 400:
        raise AssertionError(
            {
                "expected_status": 400,
                "actual_status": raw_response.status_code,
                "response": raw_response.json(),
            }
        )

    engine_handoff = _build_engine_handoff()

    accepted_response = client.post(
        "/contractor-builder/external-pressure/curated",
        json={
            "request_id": "phase-5a4-contractor-curated-pressure-probe",
            "engine_handoff_packet": engine_handoff,
        },
    )

    if accepted_response.status_code != 200:
        raise AssertionError(
            {
                "expected_status": 200,
                "actual_status": accepted_response.status_code,
                "response": accepted_response.json(),
            }
        )

    payload = accepted_response.json()

    assert payload["status"] == "ok"
    assert payload["phase"] == "Phase 5A.4"
    assert payload["child_core_id"] == "contractor_builder_v1"
    assert payload["mode"] == "advisory"
    assert payload["approval_required"] is True
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert payload["route_mode"] == "curated_external_pressure"

    authority = payload["authority"]
    assert authority["source_is_engine_curated"] is True
    assert authority["research_core_required"] is True
    assert authority["engines_required_before_child_core"] is True
    assert authority["raw_provider_payload_allowed"] is False
    assert authority["raw_research_packet_allowed"] is False
    assert authority["provider_fetch_allowed"] is False
    assert authority["workflow_mutation_allowed"] is False
    assert authority["change_creation_allowed"] is False
    assert authority["decision_creation_allowed"] is False
    assert authority["execution_allowed"] is False

    contractor_input = payload["contractor_input"]
    assert contractor_input["artifact_type"] == "contractor_builder_root_handoff_input"
    assert contractor_input["authority"]["source_is_engine_curated"] is True
    assert contractor_input["authority"]["raw_provider_payload_allowed"] is False

    external_pressure_input = payload["external_pressure_input"]
    assert external_pressure_input["signal_type"] == "contractor_external_pressure"
    assert external_pressure_input["symbol"] == "COPPER"
    assert external_pressure_input["trust_class"] in {
        "bounded_trust",
        "high_trust",
        "low_trust",
    }

    return {
        "status": "passed",
        "phase": "Phase 5A.4",
        "route": "/contractor-builder/external-pressure/curated",
        "raw_payload_rejected": raw_response.status_code == 400,
        "curated_payload_status": accepted_response.status_code,
        "child_core_id": payload["child_core_id"],
        "route_mode": payload["route_mode"],
        "execution_allowed": payload["execution_allowed"],
        "mutation_allowed": payload["mutation_allowed"],
        "symbol": external_pressure_input["symbol"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_CONTRACTOR_CURATED_EXTERNAL_PRESSURE_ROUTE_PROBE: PASS")
    print(result)
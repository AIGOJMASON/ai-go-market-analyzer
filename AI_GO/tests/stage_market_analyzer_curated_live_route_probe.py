from __future__ import annotations

import os

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


def _headers() -> dict[str, str]:
    api_key = os.getenv("AI_GO_API_KEY", "").strip()
    if not api_key:
        api_key = os.getenv("AI_GO_LOCAL_DEV_API_KEY", "AIGO-local-test").strip()
    return {"x-api-key": api_key}


def _build_engine_handoff() -> dict:
    research_packet = build_live_research_packet(
        {
            "provider": "alpha_vantage",
            "provider_kind": "market_quote",
            "source_type": "verified_api",
            "signal_type": "market_quote",
            "title": "Alpha Vantage quote signal for XLE",
            "summary": "Verified quote provider reports XLE up 1.25%.",
            "symbol": "XLE",
            "price": 91.25,
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
            "provider_payload": {
                "Global Quote": {
                    "01. symbol": "XLE",
                    "05. price": "91.25",
                    "10. change percent": "1.25%",
                }
            },
            "source_material": [
                {
                    "type": "provider_quote",
                    "provider": "alpha_vantage",
                }
            ],
            "source_refs": ["alpha_vantage:GLOBAL_QUOTE"],
            "child_core_targets": ["market_analyzer_v1"],
        }
    )

    return curate_research_packet_for_child_cores(research_packet)


def run_probe() -> dict:
    client = TestClient(app)
    headers = _headers()

    raw_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "symbol": "XLE",
            "headline": "Raw live payload should be rejected",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
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

    assert "curated" in str(raw_response.json()).lower()

    engine_handoff = _build_engine_handoff()

    accepted_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "request_id": "phase-5a3-curated-live-probe",
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

    assert isinstance(payload, dict)
    assert payload.get("core_id") == "market_analyzer_v1"
    assert payload.get("route_mode") == "pm_route"
    assert payload.get("mode") == "advisory"
    assert payload.get("execution_allowed") is False

    assert payload.get("request_id") == "phase-5a3-curated-live-probe"
    assert payload.get("receipt_id")
    assert payload.get("watcher_validation_id")
    assert payload.get("watcher_status") in {"passed", None}
    assert payload.get("closeout_id")
    assert payload.get("closeout_status") in {"accepted", None}

    return {
        "status": "passed",
        "phase": "Phase 5A.3",
        "route": "/market-analyzer/run/curated-live",
        "raw_payload_rejected": raw_response.status_code == 400,
        "curated_payload_status": accepted_response.status_code,
        "request_id": payload.get("request_id"),
        "route_mode": payload.get("route_mode"),
        "mode": payload.get("mode"),
        "execution_allowed": payload.get("execution_allowed"),
        "receipt_id_present": bool(payload.get("receipt_id")),
        "closeout_status": payload.get("closeout_status"),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_MARKET_ANALYZER_CURATED_LIVE_ROUTE_PROBE: PASS")
    print(result)
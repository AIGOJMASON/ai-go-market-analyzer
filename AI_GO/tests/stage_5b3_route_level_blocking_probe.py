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

    raw_live_response = client.post(
        "/market-analyzer/run/live",
        headers=headers,
        json={
            "request_id": "phase-5b3-raw-live-block",
            "symbol": "XLE",
            "headline": "Raw live payload must be blocked",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
        },
    )

    if raw_live_response.status_code != 403:
        raise AssertionError(
            {
                "expected_status": 403,
                "actual_status": raw_live_response.status_code,
                "response": raw_live_response.json(),
            }
        )

    blocked_detail = raw_live_response.json()
    assert "route_level_access_blocked" in str(blocked_detail)

    raw_curated_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "request_id": "phase-5b3-raw-curated-block",
            "symbol": "XLE",
            "headline": "Raw payload on curated route must be blocked",
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
        },
    )

    if raw_curated_response.status_code != 400:
        raise AssertionError(
            {
                "expected_status": 400,
                "actual_status": raw_curated_response.status_code,
                "response": raw_curated_response.json(),
            }
        )

    engine_handoff = _build_engine_handoff()

    curated_response = client.post(
        "/market-analyzer/run/curated-live",
        headers=headers,
        json={
            "request_id": "phase-5b3-curated-live-pass",
            "engine_handoff_packet": engine_handoff,
        },
    )

    if curated_response.status_code != 200:
        raise AssertionError(
            {
                "expected_status": 200,
                "actual_status": curated_response.status_code,
                "response": curated_response.json(),
            }
        )

    payload = curated_response.json()

    assert payload.get("core_id") == "market_analyzer_v1"
    assert payload.get("route_mode") == "pm_route"
    assert payload.get("mode") == "advisory"
    assert payload.get("execution_allowed") is False
    assert payload.get("approval_required") is True

    return {
        "status": "passed",
        "phase": "Phase 5B.3",
        "raw_live_blocked": raw_live_response.status_code == 403,
        "raw_curated_blocked": raw_curated_response.status_code == 400,
        "curated_live_allowed": curated_response.status_code == 200,
        "route_mode": payload.get("route_mode"),
        "execution_allowed": payload.get("execution_allowed"),
        "approval_required": payload.get("approval_required"),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5B3_ROUTE_LEVEL_BLOCKING_PROBE: PASS")
    print(result)
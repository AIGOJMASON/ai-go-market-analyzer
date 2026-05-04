from __future__ import annotations

import os

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.governance.route_enforcement import evaluate_route_level_access
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)
from AI_GO.engines.engine_signal_contract import validate_engine_interpretation_packet


def _headers() -> dict[str, str]:
    api_key = os.getenv("AI_GO_API_KEY", "").strip()
    if not api_key:
        api_key = os.getenv("AI_GO_LOCAL_DEV_API_KEY", "AIGO-local-test").strip()
    return {"x-api-key": api_key}


def _assert_status(response, expected_status: int) -> None:
    if response.status_code != expected_status:
        try:
            body = response.json()
        except Exception:
            body = response.text

        raise AssertionError(
            {
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "response": body,
            }
        )


def _build_research_packet() -> dict:
    return build_live_research_packet(
        {
            "provider": "alpha_vantage",
            "provider_kind": "market_quote",
            "source_type": "verified_api",
            "signal_type": "market_quote",
            "title": "Alpha Vantage quote signal for XLE",
            "summary": "Verified quote provider reports XLE up 1.25 percent.",
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


def _build_engine_handoff() -> dict:
    return curate_research_packet_for_child_cores(_build_research_packet())


def run_probe() -> dict:
    engine_handoff = _build_engine_handoff()

    assert engine_handoff["artifact_type"] == "curated_child_core_handoff_packet"
    assert engine_handoff["artifact_version"] == "v5C.1"
    assert engine_handoff["source_authority"] == "engines"
    assert engine_handoff["root_spine_authority"] == "root_intelligence_spine"
    assert engine_handoff["authority"]["authority_id"] == "engines"
    assert engine_handoff["authority"]["curates_before_child_core"] is True
    assert engine_handoff["target_child_core"] == "market_analyzer_v1"
    assert engine_handoff["allowed_for_child_core"] is True
    assert engine_handoff["raw_input"] is False
    assert engine_handoff["bounded"] is True
    assert engine_handoff["sealed"] is True
    assert engine_handoff.get("curated_packet")
    assert engine_handoff.get("source", {}).get("research_packet_id")
    assert engine_handoff.get("child_core_handoff", {}).get("allowed") is True

    interpretation_packet = engine_handoff["engine_interpretation_packet"]
    signal_integrity = validate_engine_interpretation_packet(interpretation_packet)

    assert signal_integrity["allowed"] is True
    assert signal_integrity["valid"] is True
    assert signal_integrity["policy"]["child_core_reinterpretation_allowed"] is False
    assert signal_integrity["policy"]["downstream_reweighting_allowed"] is False

    cross_core = evaluate_cross_core_handoff(engine_handoff)
    assert cross_core["allowed"] is True
    assert cross_core["policy"]["engine_interpretation_required"] is True
    assert cross_core["policy"]["engines_authority_required"] is True
    assert cross_core["policy"]["curates_before_child_core_required"] is True
    assert cross_core["policy"]["child_core_reinterpretation_allowed"] is False

    missing_interpretation = dict(engine_handoff)
    missing_interpretation.pop("engine_interpretation_packet", None)
    missing_interpretation.pop("engine_signal_integrity", None)

    missing_result = evaluate_cross_core_handoff(missing_interpretation)
    assert missing_result["allowed"] is False
    missing_codes = {reason["code"] for reason in missing_result["reasons"]}
    assert "engine_interpretation_missing" in missing_codes
    assert "engine_signal_integrity_failed" in missing_codes

    missing_authority = dict(engine_handoff)
    missing_authority["authority"] = dict(engine_handoff["authority"])
    missing_authority["authority"].pop("authority_id", None)

    missing_authority_result = evaluate_cross_core_handoff(missing_authority)
    assert missing_authority_result["allowed"] is False
    missing_authority_codes = {
        reason["code"] for reason in missing_authority_result["reasons"]
    }
    assert "missing_engines_authority_id" in missing_authority_codes

    route_allowed = evaluate_route_level_access(
        route="/market-analyzer/run/curated-live",
        method="POST",
        payload={"engine_handoff_packet": engine_handoff},
        actor="stage_5c1_probe",
    )
    assert route_allowed["allowed"] is True
    assert route_allowed["policy"]["curated_live_requires_engine_interpretation"] is True

    route_blocked = evaluate_route_level_access(
        route="/market-analyzer/run/curated-live",
        method="POST",
        payload={"engine_handoff_packet": missing_interpretation},
        actor="stage_5c1_probe",
    )
    assert route_blocked["allowed"] is False
    route_codes = {reason["code"] for reason in route_blocked["reasons"]}
    assert "engine_interpretation_packet_missing" in route_codes
    assert "engine_signal_integrity_failed" in route_codes

    client = TestClient(app)
    response = client.post(
        "/market-analyzer/run/curated-live",
        headers=_headers(),
        json={
            "request_id": "phase-5c1-engine-contract-pass",
            "engine_handoff_packet": engine_handoff,
        },
    )

    _assert_status(response, 200)

    payload = response.json()
    assert payload["execution_allowed"] is False
    assert (
        payload.get("approval_required") is True
        or payload["governance_panel"]["approval_required"] is True
    )

    return {
        "status": "passed",
        "phase": "Phase 5C.1",
        "engine_contract_valid": signal_integrity["allowed"],
        "cross_core_allowed_with_interpretation": cross_core["allowed"],
        "cross_core_blocks_missing_interpretation": missing_result["allowed"] is False,
        "cross_core_blocks_missing_engines_authority": missing_authority_result["allowed"] is False,
        "route_blocks_missing_interpretation": route_blocked["allowed"] is False,
        "curated_route_status": response.status_code,
        "execution_allowed": payload["execution_allowed"],
        "approval_required": payload.get("approval_required")
        or payload.get("governance_panel", {}).get("approval_required"),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5C1_ENGINE_CONTRACT_PROBE: PASS")
    print(result)
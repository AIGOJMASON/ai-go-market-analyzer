from __future__ import annotations

import os
from copy import deepcopy

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.governance.route_enforcement import evaluate_route_level_access
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)
from AI_GO.engines.engine_confidence_conservation import (
    evaluate_engine_confidence_conservation,
)
from AI_GO.engines.engine_drift_guard import evaluate_engine_drift
from AI_GO.engines.engine_output_registry import validate_engine_output_registry
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
            "provider": "manual_watchlist_note",
            "provider_kind": "operator_context",
            "source_type": "rss_feed",
            "signal_type": "market_quote",
            "title": "Bounded RSS-style signal for XLE",
            "summary": "RSS-style source reports XLE up 1.25 percent.",
            "symbol": "XLE",
            "price": 91.25,
            "price_change_pct": 1.25,
            "sector": "energy",
            "confirmation": "partial",
            "provider_payload": {},
            "source_material": [
                {
                    "type": "rss_summary",
                    "provider": "manual_watchlist_note",
                }
            ],
            "source_refs": ["rss_feed:manual_watchlist_note"],
            "child_core_targets": ["market_analyzer_v1"],
        }
    )


def run_probe() -> dict:
    research_packet = _build_research_packet()
    handoff = curate_research_packet_for_child_cores(research_packet)
    interpretation_packet = handoff["engine_interpretation_packet"]

    assert handoff["artifact_version"] == "v5C.4"
    assert handoff["source_authority"] == "engines"
    assert handoff["root_spine_authority"] == "root_intelligence_spine"
    assert handoff["authority"]["authority_id"] == "engines"
    assert handoff["authority"]["curates_before_child_core"] is True
    assert handoff["engine_drift_seal"]["seal_hash"]
    assert handoff["raw_input"] is False
    assert handoff["bounded"] is True
    assert handoff["sealed"] is True

    signal_integrity = validate_engine_interpretation_packet(interpretation_packet)
    assert signal_integrity["allowed"] is True

    registry = validate_engine_output_registry(interpretation_packet)
    assert registry["allowed"] is True

    conservation = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=interpretation_packet,
    )
    assert conservation["allowed"] is True

    drift = evaluate_engine_drift(
        original_handoff_packet=handoff,
        candidate_handoff_packet=deepcopy(handoff),
    )
    assert drift["allowed"] is True

    cross_core = evaluate_cross_core_handoff(handoff)
    assert cross_core["allowed"] is True
    assert cross_core["policy"]["engine_interpretation_required"] is True
    assert cross_core["policy"]["engine_output_registry_required"] is True
    assert cross_core["policy"]["engine_confidence_conservation_required"] is True
    assert cross_core["policy"]["downstream_reweighting_allowed"] is False
    assert cross_core["policy"]["child_core_reinterpretation_allowed"] is False

    missing_interpretation = deepcopy(handoff)
    missing_interpretation.pop("engine_interpretation_packet", None)
    missing_interpretation.pop("engine_signal_integrity", None)
    missing_interpretation.pop("engine_output_registry", None)

    missing_interpretation_result = evaluate_cross_core_handoff(missing_interpretation)
    assert missing_interpretation_result["allowed"] is False
    missing_codes = {
        reason["code"] for reason in missing_interpretation_result["reasons"]
    }
    assert "engine_interpretation_missing" in missing_codes
    assert "engine_signal_integrity_failed" in missing_codes
    assert "engine_output_registry_failed" in missing_codes

    reclassified = deepcopy(handoff)
    reclassified["engine_interpretation_packet"]["interpretation"][
        "classification"
    ] = "unauthorized_reclassification"

    reclassified_result = evaluate_cross_core_handoff(
        reclassified,
        original_handoff_packet=handoff,
    )
    assert reclassified_result["allowed"] is False
    reclassified_codes = {reason["code"] for reason in reclassified_result["reasons"]}
    assert "engine_drift_detected" in reclassified_codes

    invented_type = deepcopy(handoff)
    invented_type["engine_interpretation_packet"]["interpretation"][
        "type"
    ] = "invented_strategy_layer"

    invented_type_result = evaluate_cross_core_handoff(invented_type)
    assert invented_type_result["allowed"] is False
    invented_type_codes = {reason["code"] for reason in invented_type_result["reasons"]}
    assert "engine_output_registry_failed" in invented_type_codes

    inflated_confidence = deepcopy(handoff)
    inflated_confidence["engine_interpretation_packet"]["interpretation"][
        "confidence"
    ] = min(float(research_packet["trust"]["pre_weight"]) + 0.25, 1.0)

    inflated_confidence_result = evaluate_cross_core_handoff(inflated_confidence)
    assert inflated_confidence_result["allowed"] is False
    inflated_confidence_codes = {
        reason["code"] for reason in inflated_confidence_result["reasons"]
    }
    assert "engine_confidence_conservation_failed" in inflated_confidence_codes

    inflated_weight = deepcopy(handoff)
    inflated_weight["engine_interpretation_packet"]["interpretation"]["weight"] = min(
        float(research_packet["trust"]["pre_weight"]) + 0.25,
        1.0,
    )

    inflated_weight_result = evaluate_cross_core_handoff(inflated_weight)
    assert inflated_weight_result["allowed"] is False
    inflated_weight_codes = {
        reason["code"] for reason in inflated_weight_result["reasons"]
    }
    assert "engine_confidence_conservation_failed" in inflated_weight_codes

    route_allowed = evaluate_route_level_access(
        route="/market-analyzer/run/curated-live",
        method="POST",
        payload={"engine_handoff_packet": handoff},
        actor="stage_5c5_probe",
    )
    assert route_allowed["allowed"] is True

    route_missing_interpretation = evaluate_route_level_access(
        route="/market-analyzer/run/curated-live",
        method="POST",
        payload={"engine_handoff_packet": missing_interpretation},
        actor="stage_5c5_probe",
    )
    assert route_missing_interpretation["allowed"] is False

    client = TestClient(app)
    response = client.post(
        "/market-analyzer/run/curated-live",
        headers=_headers(),
        json={
            "request_id": "phase-5c5-full-engine-deepening-regression",
            "engine_handoff_packet": handoff,
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
        "phase": "Phase 5C.5",
        "signal_contract_valid": signal_integrity["allowed"],
        "engine_registry_valid": registry["allowed"],
        "confidence_conserved": conservation["allowed"],
        "drift_guard_allows_unchanged": drift["allowed"],
        "cross_core_allows_valid_handoff": cross_core["allowed"],
        "missing_interpretation_blocked": missing_interpretation_result["allowed"] is False,
        "reclassification_blocked": reclassified_result["allowed"] is False,
        "invented_type_blocked": invented_type_result["allowed"] is False,
        "inflated_confidence_blocked": inflated_confidence_result["allowed"] is False,
        "inflated_weight_blocked": inflated_weight_result["allowed"] is False,
        "route_allows_valid_handoff": route_allowed["allowed"],
        "route_blocks_missing_interpretation": route_missing_interpretation["allowed"] is False,
        "curated_route_status": response.status_code,
        "execution_allowed": payload["execution_allowed"],
        "approval_required": payload.get("approval_required")
        or payload.get("governance_panel", {}).get("approval_required"),
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5C5_FULL_ENGINE_DEEPENING_REGRESSION_PROBE: PASS")
    print(result)
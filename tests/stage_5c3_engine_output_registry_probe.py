from __future__ import annotations

from copy import deepcopy

from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)
from AI_GO.engines.engine_output_registry import validate_engine_output_registry


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
    handoff = _build_engine_handoff()
    interpretation_packet = handoff["engine_interpretation_packet"]

    registry = validate_engine_output_registry(interpretation_packet)
    assert registry["allowed"] is True
    assert registry["artifact_version"] == "v5C.3"

    cross_core = evaluate_cross_core_handoff(handoff)
    assert cross_core["allowed"] is True
    assert cross_core["policy"]["engine_output_registry_required"] is True

    invented_type = deepcopy(interpretation_packet)
    invented_type["interpretation"]["type"] = "invented_strategy_layer"

    invented_type_registry = validate_engine_output_registry(invented_type)
    assert invented_type_registry["allowed"] is False
    invented_codes = {reason["code"] for reason in invented_type_registry["reasons"]}
    assert "unapproved_interpretation_type" in invented_codes

    invented_type_handoff = deepcopy(handoff)
    invented_type_handoff["engine_interpretation_packet"] = invented_type
    invented_type_cross_core = evaluate_cross_core_handoff(invented_type_handoff)
    assert invented_type_cross_core["allowed"] is False
    invented_cross_codes = {
        reason["code"] for reason in invented_type_cross_core["reasons"]
    }
    assert "engine_output_registry_failed" in invented_cross_codes

    invented_artifact = deepcopy(interpretation_packet)
    invented_artifact["artifact_type"] = "engine_freeform_strategy_packet"

    invented_artifact_registry = validate_engine_output_registry(invented_artifact)
    assert invented_artifact_registry["allowed"] is False
    artifact_codes = {
        reason["code"] for reason in invented_artifact_registry["reasons"]
    }
    assert "unapproved_engine_artifact_type" in artifact_codes

    forbidden_key = deepcopy(interpretation_packet)
    forbidden_key["execution_command"] = {"action": "dispatch"}

    forbidden_key_registry = validate_engine_output_registry(forbidden_key)
    assert forbidden_key_registry["allowed"] is False
    forbidden_codes = {reason["code"] for reason in forbidden_key_registry["reasons"]}
    assert "forbidden_engine_output_keys" in forbidden_codes

    unknown_engine = deepcopy(interpretation_packet)
    unknown_engine["engine_id"] = "unregistered_engine"

    unknown_engine_registry = validate_engine_output_registry(unknown_engine)
    assert unknown_engine_registry["allowed"] is False
    unknown_codes = {reason["code"] for reason in unknown_engine_registry["reasons"]}
    assert "unregistered_engine_id" in unknown_codes

    return {
        "status": "passed",
        "phase": "Phase 5C.3",
        "registered_output_allowed": registry["allowed"],
        "cross_core_allows_registered_output": cross_core["allowed"],
        "invented_interpretation_type_blocked": invented_type_registry["allowed"] is False,
        "cross_core_blocks_invented_type": invented_type_cross_core["allowed"] is False,
        "invented_artifact_type_blocked": invented_artifact_registry["allowed"] is False,
        "forbidden_execution_key_blocked": forbidden_key_registry["allowed"] is False,
        "unregistered_engine_blocked": unknown_engine_registry["allowed"] is False,
        "execution_allowed": False,
        "approval_required": True,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5C3_ENGINE_OUTPUT_REGISTRY_PROBE: PASS")
    print(result)
from __future__ import annotations

from copy import deepcopy

from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)
from AI_GO.engines.engine_confidence_conservation import (
    evaluate_engine_confidence_conservation,
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

    pre_weight = float(research_packet["trust"]["pre_weight"])
    assert pre_weight < 1.0

    conservation = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=interpretation_packet,
    )
    assert conservation["allowed"] is True
    assert conservation["artifact_version"] == "v5C.4"

    cross_core = evaluate_cross_core_handoff(handoff)
    assert cross_core["allowed"] is True
    assert cross_core["policy"]["engine_confidence_conservation_required"] is True

    inflated_confidence = deepcopy(handoff)
    inflated_confidence["engine_interpretation_packet"]["interpretation"][
        "confidence"
    ] = min(pre_weight + 0.25, 1.0)

    inflated_confidence_cross_core = evaluate_cross_core_handoff(inflated_confidence)
    assert inflated_confidence_cross_core["allowed"] is False
    inflated_confidence_codes = {
        reason["code"] for reason in inflated_confidence_cross_core["reasons"]
    }
    assert "engine_confidence_conservation_failed" in inflated_confidence_codes

    inflated_weight = deepcopy(handoff)
    inflated_weight["engine_interpretation_packet"]["interpretation"][
        "weight"
    ] = min(pre_weight + 0.25, 1.0)

    inflated_weight_cross_core = evaluate_cross_core_handoff(inflated_weight)
    assert inflated_weight_cross_core["allowed"] is False
    inflated_weight_codes = {
        reason["code"] for reason in inflated_weight_cross_core["reasons"]
    }
    assert "engine_confidence_conservation_failed" in inflated_weight_codes

    direct_conservation_fail = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=inflated_confidence["engine_interpretation_packet"],
    )
    assert direct_conservation_fail["allowed"] is False
    direct_codes = {reason["code"] for reason in direct_conservation_fail["reasons"]}
    assert "unearned_confidence_detected" in direct_codes

    uplifted = deepcopy(interpretation_packet)
    uplifted["interpretation"]["confidence"] = min(pre_weight + 0.05, 1.0)
    uplifted["interpretation"]["weight"] = min(pre_weight + 0.05, 1.0)

    uplifted_conservation = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=uplifted,
        uplift_record={
            "approved": True,
            "reason": "multi_source_confirmation",
            "amount": 0.05,
        },
    )
    assert uplifted_conservation["allowed"] is True

    bad_uplift = evaluate_engine_confidence_conservation(
        research_packet=research_packet,
        engine_interpretation_packet=uplifted,
        uplift_record={
            "approved": True,
            "reason": "invented_reason",
            "amount": 0.05,
        },
    )
    assert bad_uplift["allowed"] is False

    return {
        "status": "passed",
        "phase": "Phase 5C.4",
        "research_pre_weight": pre_weight,
        "conserved_output_allowed": conservation["allowed"],
        "cross_core_allows_conserved_output": cross_core["allowed"],
        "inflated_confidence_blocked": inflated_confidence_cross_core["allowed"] is False,
        "inflated_weight_blocked": inflated_weight_cross_core["allowed"] is False,
        "approved_uplift_allowed": uplifted_conservation["allowed"],
        "bad_uplift_blocked": bad_uplift["allowed"] is False,
        "execution_allowed": False,
        "approval_required": True,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5C4_ENGINE_CONFIDENCE_CONSERVATION_PROBE: PASS")
    print(result)
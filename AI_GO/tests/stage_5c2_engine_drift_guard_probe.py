from __future__ import annotations

from copy import deepcopy

from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)
from AI_GO.engines.engine_drift_guard import evaluate_engine_drift


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
    original = _build_engine_handoff()

    assert original["artifact_version"] == "v5C.2"
    assert original["engine_drift_seal"]["artifact_version"] == "v5C.2"
    assert original["engine_drift_seal"]["seal_hash"]

    unchanged_candidate = deepcopy(original)

    unchanged_drift = evaluate_engine_drift(
        original_handoff_packet=original,
        candidate_handoff_packet=unchanged_candidate,
    )
    assert unchanged_drift["allowed"] is True

    unchanged_cross_core = evaluate_cross_core_handoff(
        unchanged_candidate,
        original_handoff_packet=original,
    )
    assert unchanged_cross_core["allowed"] is True

    reclassified_candidate = deepcopy(original)
    reclassified_candidate["engine_interpretation_packet"]["interpretation"][
        "classification"
    ] = "unauthorized_reclassification"

    reclassified_drift = evaluate_engine_drift(
        original_handoff_packet=original,
        candidate_handoff_packet=reclassified_candidate,
    )
    assert reclassified_drift["allowed"] is False
    assert "engine_interpretation_drift_detected" in reclassified_drift["errors"]

    reclassified_cross_core = evaluate_cross_core_handoff(
        reclassified_candidate,
        original_handoff_packet=original,
    )
    assert reclassified_cross_core["allowed"] is False
    reclassified_codes = {
        reason["code"] for reason in reclassified_cross_core["reasons"]
    }
    assert "engine_drift_detected" in reclassified_codes

    reweighted_candidate = deepcopy(original)
    reweighted_candidate["engine_interpretation_packet"]["interpretation"][
        "weight"
    ] = 0.99
    reweighted_candidate["engine_interpretation_packet"]["interpretation"][
        "weight_band"
    ] = "high"

    reweighted_drift = evaluate_engine_drift(
        original_handoff_packet=original,
        candidate_handoff_packet=reweighted_candidate,
    )
    assert reweighted_drift["allowed"] is False
    assert "engine_interpretation_drift_detected" in reweighted_drift["errors"]

    redirected_candidate = deepcopy(original)
    redirected_candidate["engine_interpretation_packet"]["interpretation"][
        "direction"
    ] = "negative"

    redirected_drift = evaluate_engine_drift(
        original_handoff_packet=original,
        candidate_handoff_packet=redirected_candidate,
    )
    assert redirected_drift["allowed"] is False
    assert "engine_interpretation_drift_detected" in redirected_drift["errors"]

    return {
        "status": "passed",
        "phase": "Phase 5C.2",
        "unchanged_candidate_allowed": unchanged_drift["allowed"],
        "cross_core_allows_unchanged_candidate": unchanged_cross_core["allowed"],
        "reclassification_blocked": reclassified_drift["allowed"] is False,
        "cross_core_blocks_reclassification": reclassified_cross_core["allowed"] is False,
        "reweighting_blocked": reweighted_drift["allowed"] is False,
        "direction_mutation_blocked": redirected_drift["allowed"] is False,
        "execution_allowed": False,
        "approval_required": True,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5C2_ENGINE_DRIFT_GUARD_PROBE: PASS")
    print(result)
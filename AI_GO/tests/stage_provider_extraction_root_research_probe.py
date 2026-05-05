from __future__ import annotations

from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.core.root_intelligence_spine import run_root_intelligence_spine
from AI_GO.engines.curated_child_core_handoff_engine import (
    curate_research_packet_for_child_cores,
)


def run_probe() -> dict:
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
            "provider_payload": {"Global Quote": {"01. symbol": "XLE"}},
            "source_material": [{"type": "provider_quote", "provider": "alpha_vantage"}],
            "source_refs": ["alpha_vantage:GLOBAL_QUOTE"],
            "child_core_targets": ["market_analyzer_v1", "contractor_builder_v1"],
        }
    )

    assert research_packet["authority"]["authority_id"] == "RESEARCH_CORE"
    assert research_packet["authority"]["multi_child_core_source"] is True
    assert research_packet["routing"]["must_pass_engines_before_child_core"] is True
    assert research_packet["screening"]["valid"] is True

    handoff_packet = curate_research_packet_for_child_cores(research_packet)

    assert handoff_packet["authority"]["authority_id"] == "engines"
    assert handoff_packet["authority"]["curates_before_child_core"] is True
    assert handoff_packet["authority"]["multi_child_core_handoff"] is True
    assert handoff_packet["child_core_handoff"]["allowed"] is True
    assert "market_analyzer_v1" in handoff_packet["child_core_handoff"]["targets"]
    assert "contractor_builder_v1" in handoff_packet["child_core_handoff"]["targets"]

    spine_packet = run_root_intelligence_spine(
        research_packet=research_packet,
        curation_approved=False,
    )

    assert spine_packet["phase"] == "Phase 5A.1"
    assert spine_packet["authority"]["provider_clients_inside_child_core_allowed"] is False
    assert spine_packet["authority"]["raw_provider_payload_to_child_core_allowed"] is False
    assert spine_packet["authority"]["engines_required_before_child_core"] is True
    assert spine_packet["summary"]["handoff_allowed"] is True
    assert spine_packet["summary"]["external_memory_status"] == "skipped"

    return {
        "status": "passed",
        "phase": "Phase 5A.1",
        "research_authority": research_packet["authority"]["authority_id"],
        "engine_authority": handoff_packet["authority"]["authority_id"],
        "targets": spine_packet["summary"]["targets"],
        "handoff_allowed": spine_packet["summary"]["handoff_allowed"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_PROVIDER_EXTRACTION_ROOT_RESEARCH_PROBE: PASS")
    print(result)
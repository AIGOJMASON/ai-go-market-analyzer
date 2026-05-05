from __future__ import annotations

from AI_GO.child_cores.contractor_builder_v1.adapters.root_handoff_adapter import (
    build_contractor_builder_input_from_root_handoff,
)
from AI_GO.child_cores.market_analyzer_v1.adapters.root_handoff_adapter import (
    build_market_analyzer_input_from_root_handoff,
)
from AI_GO.core.child_core_handoff.consumption_adapter import (
    ChildCoreConsumptionAdapterError,
    build_child_core_consumption_packet,
)
from AI_GO.core.research.live_research_gateway import build_live_research_packet
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

    engine_handoff = curate_research_packet_for_child_cores(research_packet)

    market_consumption = build_child_core_consumption_packet(
        child_core_id="market_analyzer_v1",
        engine_handoff_packet=engine_handoff,
    )
    contractor_consumption = build_child_core_consumption_packet(
        child_core_id="contractor_builder_v1",
        engine_handoff_packet=engine_handoff,
    )

    assert market_consumption["authority"]["receives_engine_curated_only"] is True
    assert market_consumption["authority"]["raw_provider_payload_allowed"] is False
    assert market_consumption["authority"]["raw_research_packet_allowed"] is False
    assert market_consumption["authority"]["can_fetch_provider"] is False

    assert contractor_consumption["authority"]["receives_engine_curated_only"] is True
    assert contractor_consumption["authority"]["raw_provider_payload_allowed"] is False
    assert contractor_consumption["authority"]["can_fetch_provider"] is False

    market_input = build_market_analyzer_input_from_root_handoff(engine_handoff)
    contractor_input = build_contractor_builder_input_from_root_handoff(engine_handoff)

    assert market_input["artifact_type"] == "market_analyzer_root_handoff_input"
    assert market_input["authority"]["source_is_engine_curated"] is True
    assert market_input["authority"]["raw_provider_payload_allowed"] is False
    assert market_input["authority"]["direct_live_post_allowed"] is False
    assert market_input["live_input"]["symbol"] == "XLE"

    assert contractor_input["artifact_type"] == "contractor_builder_root_handoff_input"
    assert contractor_input["authority"]["source_is_engine_curated"] is True
    assert contractor_input["authority"]["raw_provider_payload_allowed"] is False
    assert contractor_input["external_pressure_input"]["symbol"] == "XLE"

    try:
        build_child_core_consumption_packet(
            child_core_id="unauthorized_child_core",
            engine_handoff_packet=engine_handoff,
        )
        raise AssertionError("unauthorized child core should not receive handoff")
    except ChildCoreConsumptionAdapterError as exc:
        assert "child_core_not_authorized_for_handoff" in str(exc)

    return {
        "status": "passed",
        "phase": "Phase 5A.2",
        "market_adapter": market_input["artifact_type"],
        "contractor_adapter": contractor_input["artifact_type"],
        "symbol": market_input["live_input"]["symbol"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_CHILD_CORE_CONSUMPTION_ADAPTER_PROBE: PASS")
    print(result)
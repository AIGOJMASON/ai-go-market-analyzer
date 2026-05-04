from __future__ import annotations

from typing import Any

from AI_GO.core.child_core_handoff.consumption_adapter import (
    build_child_core_consumption_packet,
)


def build_market_analyzer_input_from_root_handoff(
    engine_handoff_packet: dict[str, Any],
) -> dict[str, Any]:
    consumption_packet = build_child_core_consumption_packet(
        child_core_id="market_analyzer_v1",
        engine_handoff_packet=engine_handoff_packet,
    )

    curated = dict(consumption_packet.get("curated_input", {}))

    return {
        "artifact_type": "market_analyzer_root_handoff_input",
        "sealed": True,
        "source_consumption_adapter_id": consumption_packet.get("adapter_id"),
        "child_core_id": "market_analyzer_v1",
        "authority": {
            "source_is_engine_curated": True,
            "raw_provider_payload_allowed": False,
            "provider_fetch_allowed": False,
            "direct_live_post_allowed": False,
            "execution_allowed": False,
        },
        "live_input": {
            "request_id": consumption_packet.get("adapter_id"),
            "symbol": curated.get("symbol", ""),
            "headline": curated.get("title", ""),
            "summary": curated.get("summary", ""),
            "price_change_pct": curated.get("price_change_pct", 0),
            "sector": curated.get("sector", "unknown"),
            "confirmation": curated.get("confirmation", "partial"),
            "observed_at": curated.get("observed_at", ""),
            "source": "root_intelligence_spine",
            "source_refs": curated.get("source_refs", []),
            "pre_weight": curated.get("pre_weight", 0),
            "trust_class": curated.get("trust_class", ""),
            "interpretation_class": curated.get("interpretation_class", ""),
        },
    }
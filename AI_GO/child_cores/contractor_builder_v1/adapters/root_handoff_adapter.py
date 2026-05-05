from __future__ import annotations

from typing import Any

from AI_GO.core.child_core_handoff.consumption_adapter import (
    build_child_core_consumption_packet,
)


def build_contractor_builder_input_from_root_handoff(
    engine_handoff_packet: dict[str, Any],
) -> dict[str, Any]:
    consumption_packet = build_child_core_consumption_packet(
        child_core_id="contractor_builder_v1",
        engine_handoff_packet=engine_handoff_packet,
    )

    curated = dict(consumption_packet.get("curated_input", {}))

    return {
        "artifact_type": "contractor_builder_root_handoff_input",
        "sealed": True,
        "source_consumption_adapter_id": consumption_packet.get("adapter_id"),
        "child_core_id": "contractor_builder_v1",
        "authority": {
            "source_is_engine_curated": True,
            "raw_provider_payload_allowed": False,
            "provider_fetch_allowed": False,
            "execution_allowed": False,
        },
        "external_pressure_input": {
            "signal_type": curated.get("signal_type", ""),
            "title": curated.get("title", ""),
            "summary": curated.get("summary", ""),
            "symbol": curated.get("symbol", ""),
            "symbols": curated.get("symbols", []),
            "price": curated.get("price"),
            "price_change_pct": curated.get("price_change_pct"),
            "sector": curated.get("sector", "unknown"),
            "confirmation": curated.get("confirmation", "partial"),
            "observed_at": curated.get("observed_at", ""),
            "source_refs": curated.get("source_refs", []),
            "pre_weight": curated.get("pre_weight", 0),
            "trust_class": curated.get("trust_class", ""),
            "interpretation_class": curated.get("interpretation_class", ""),
        },
    }
from __future__ import annotations

from typing import Any, Dict

from PM_CORE.inheritance.inheritance_packet_builder import (
    build_inheritance_packet,
    persist_inheritance_packet,
)


def materialize_inheritance_from_interpretation(
    *,
    research_packet: Dict[str, Any],
    interpretation: Dict[str, Any],
    propagation_result: Dict[str, Any],
) -> Dict[str, Any]:
    if propagation_result.get("decision") != "propagate_to_inheritance":
        return {
            "status": "skipped",
            "reason": "propagation_not_authorized",
            "propagation_result": propagation_result,
        }

    inheritance_packet = build_inheritance_packet(
        research_packet=research_packet,
        interpretation=interpretation,
        propagation_result=propagation_result,
    )

    persistence_result = persist_inheritance_packet(inheritance_packet)

    return {
        "status": "recorded",
        "inheritance_packet_id": persistence_result.get("inheritance_packet_id"),
        "inheritance_packet_path": persistence_result.get("inheritance_packet_path"),
        "inheritance_packet": persistence_result.get("inheritance_packet"),
        "propagation_result": propagation_result,
    }
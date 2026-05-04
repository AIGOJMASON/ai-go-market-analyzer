from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_execution_intake_policy import (
    build_child_core_execution_packet,
)


def construct_child_core_execution_packet(
    execution_fusion_record: dict,
    target_core: str,
) -> dict:
    packet = build_child_core_execution_packet(
        execution_fusion_record=execution_fusion_record,
        target_core=target_core,
    )
    packet["receipt"]["packet_id"] = packet["packet_id"]
    return packet
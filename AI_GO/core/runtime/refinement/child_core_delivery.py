from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_delivery_policy import (
    build_child_core_delivery_packet,
)


def construct_child_core_delivery_packet(adapter_packet: dict) -> dict:
    return build_child_core_delivery_packet(adapter_packet)
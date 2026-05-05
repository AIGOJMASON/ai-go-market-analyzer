from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_adapter_policy import (
    build_child_core_adapter_packet,
)


def construct_child_core_adapter_packet(execution_result: dict) -> dict:
    return build_child_core_adapter_packet(execution_result)
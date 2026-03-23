from __future__ import annotations

from AI_GO.core.runtime.refinement.child_core_execution_surface_policy import (
    build_child_core_execution_result,
)


def construct_child_core_execution_result(packet: dict) -> dict:
    result = build_child_core_execution_result(packet)
    result["receipt"]["result_id"] = result["result_id"]
    return result
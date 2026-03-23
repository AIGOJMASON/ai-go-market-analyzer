"""
Stage 76 child-core adapter layer.

Consumes a sealed child_core_execution_result and emits a sealed
child_core_adapter_packet for downstream target-specific adapters.
"""

from __future__ import annotations

from typing import Any, Dict

from .child_core_adapter_policy import (
    build_child_core_adapter_packet,
    validate_execution_result,
)


def build_child_core_adapter_packet_from_result(
    child_core_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    validate_execution_result(child_core_execution_result)
    return build_child_core_adapter_packet(child_core_execution_result)
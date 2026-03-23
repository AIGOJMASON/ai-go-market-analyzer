"""
Stage 77 target-specific adapter surface.

Consumes a sealed child_core_adapter_packet and emits a sealed
target_specific_adapter_packet for downstream target-specific implementation.
"""

from __future__ import annotations

from typing import Any, Dict

from .target_specific_adapter_surface_policy import (
    build_target_specific_adapter_packet,
    validate_adapter_packet,
)


def build_target_specific_adapter_packet_from_adapter(
    child_core_adapter_packet: Dict[str, Any],
) -> Dict[str, Any]:
    validate_adapter_packet(child_core_adapter_packet)
    return build_target_specific_adapter_packet(child_core_adapter_packet)
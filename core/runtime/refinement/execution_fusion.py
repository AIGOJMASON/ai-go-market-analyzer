"""
Stage 73 execution fusion.

Consumes sealed Rosetta and Curved Mirror runtime execution states and emits
a sealed execution_fusion_record for downstream child-core integration.
"""

from __future__ import annotations

from typing import Any, Dict

from .execution_fusion_policy import (
    build_execution_fusion_record,
    validate_case_continuity,
    validate_combined_weight,
    validate_curved_mirror_execution_state,
    validate_rosetta_execution_state,
)


def build_fused_execution_record(
    rosetta_runtime_execution_state: Dict[str, Any],
    curved_mirror_runtime_execution_state: Dict[str, Any],
) -> Dict[str, Any]:
    validate_rosetta_execution_state(rosetta_runtime_execution_state)
    validate_curved_mirror_execution_state(curved_mirror_runtime_execution_state)
    validate_case_continuity(
        rosetta_runtime_execution_state,
        curved_mirror_runtime_execution_state,
    )
    validate_combined_weight(
        rosetta_runtime_execution_state,
        curved_mirror_runtime_execution_state,
    )

    return build_execution_fusion_record(
        rosetta_runtime_execution_state,
        curved_mirror_runtime_execution_state,
    )
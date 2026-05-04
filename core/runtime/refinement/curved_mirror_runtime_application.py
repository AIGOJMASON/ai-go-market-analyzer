"""
Stage 72 Curved Mirror runtime application.

Consumes a sealed runtime_refinement_coupling_record and emits a sealed
curved_mirror_runtime_execution_state.

This layer applies refinement to Curved Mirror runtime behavior within already-
authorized allocation bounds.
"""

from __future__ import annotations

from typing import Any, Dict

from .curved_mirror_runtime_application_policy import (
    build_execution_state,
    validate_curved_mirror_channel,
    validate_input,
    validate_no_cross_consumer_leakage,
)


def build_curved_mirror_runtime_execution_state(
    runtime_refinement_coupling_record: Dict[str, Any],
) -> Dict[str, Any]:
    validate_input(runtime_refinement_coupling_record)
    validate_curved_mirror_channel(runtime_refinement_coupling_record)
    validate_no_cross_consumer_leakage(runtime_refinement_coupling_record)

    return build_execution_state(runtime_refinement_coupling_record)
"""
Stage 71 Rosetta runtime application.

Consumes a sealed runtime_refinement_coupling_record and emits a sealed
rosetta_runtime_execution_state.

This layer applies refinement to Rosetta runtime behavior within already-
authorized allocation bounds.
"""

from __future__ import annotations

from typing import Any, Dict

from .rosetta_runtime_application_policy import (
    build_execution_state,
    validate_input,
    validate_no_cross_consumer_leakage,
    validate_rosetta_channel,
)


def build_rosetta_runtime_execution_state(
    runtime_refinement_coupling_record: Dict[str, Any],
) -> Dict[str, Any]:
    validate_input(runtime_refinement_coupling_record)
    validate_rosetta_channel(runtime_refinement_coupling_record)
    validate_no_cross_consumer_leakage(runtime_refinement_coupling_record)

    return build_execution_state(runtime_refinement_coupling_record)
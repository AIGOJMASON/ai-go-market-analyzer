from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.runtime.refinement.refinement_arbitrator_registry import (
    REFINEMENT_ARBITRATOR_REGISTRY,
)


def build_refinement_arbitrator_packet(
    *,
    core_id: str,
    refinement_mode: str,
    confidence_adjustment: str,
    risk_flags: List[str],
    reasoning_summary: str,
    narrative_summary: str,
    source_lineage: Dict[str, Any],
    analog_signal: str | None = None,
    historical_failure_bias: str | None = None,
    historical_success_bias: str | None = None,
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    if refinement_mode not in REFINEMENT_ARBITRATOR_REGISTRY["allowed_refinement_modes"]:
        raise ValueError("invalid refinement_mode")

    if confidence_adjustment not in REFINEMENT_ARBITRATOR_REGISTRY["allowed_confidence_adjustments"]:
        raise ValueError("invalid confidence_adjustment")

    return {
        "artifact_type": REFINEMENT_ARBITRATOR_REGISTRY["artifact_type"],
        "artifact_version": REFINEMENT_ARBITRATOR_REGISTRY["artifact_version"],
        "sealed": True,
        "core_id": core_id,
        "refinement_mode": refinement_mode,
        "confidence_adjustment": confidence_adjustment,
        "risk_flags": list(risk_flags),
        "reasoning_summary": reasoning_summary,
        "narrative_summary": narrative_summary,
        "analog_signal": analog_signal,
        "historical_failure_bias": historical_failure_bias,
        "historical_success_bias": historical_success_bias,
        "notes": list(notes or []),
        "source_lineage": dict(source_lineage),
    }
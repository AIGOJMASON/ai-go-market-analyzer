from __future__ import annotations

REFINEMENT_ARBITRATOR_REGISTRY = {
    "artifact_type": "refinement_arbitrator_packet",
    "artifact_version": "v1",
    "core_id": "market_analyzer_v1",
    "allowed_refinement_modes": [
        "annotation_only",
        "confidence_conditioning",
    ],
    "allowed_confidence_adjustments": [
        "up",
        "down",
        "none",
    ],
}
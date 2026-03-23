from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EngineSurface:
    engine_id: str
    authority_class: str
    entrypoint: str
    accepted_artifacts: List[str]
    emitted_artifacts: List[str]
    notes: str


ENGINE_SURFACES: Dict[str, EngineSurface] = {
    "curved_mirror": EngineSurface(
        engine_id="curved_mirror",
        authority_class="reasoning_refinement",
        entrypoint="AI_GO/engines/curved_mirror/engine.py",
        accepted_artifacts=["screened_research_packet", "refinement_request"],
        emitted_artifacts=["reasoning_refinement_result"],
        notes="Reasoning-refinement engine surface.",
    ),
    "rosetta": EngineSurface(
        engine_id="rosetta",
        authority_class="narrative_refinement",
        entrypoint="AI_GO/engines/rosetta/engine.py",
        accepted_artifacts=["screened_research_packet", "refinement_request"],
        emitted_artifacts=["narrative_refinement_result"],
        notes="Narrative-refinement engine surface.",
    ),
    "refinement_arbitrator": EngineSurface(
        engine_id="refinement_arbitrator",
        authority_class="refinement_governance",
        entrypoint="AI_GO/engines/refinement_arbitrator/engine.py:run_arbitration",
        accepted_artifacts=["screened_research_packet"],
        emitted_artifacts=["arbitration_decision_packet", "arbitration_receipt"],
        notes="Stage 16 propagation-governance engine that evaluates screened research before PM intake.",
    ),
}


def get_engine_surface(engine_id: str) -> EngineSurface:
    if engine_id not in ENGINE_SURFACES:
        raise KeyError(f"Unknown engine surface: {engine_id}")
    return ENGINE_SURFACES[engine_id]


def list_engine_surfaces() -> List[str]:
    return sorted(ENGINE_SURFACES.keys())
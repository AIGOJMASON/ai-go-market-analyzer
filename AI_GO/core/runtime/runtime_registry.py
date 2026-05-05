from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RuntimeSurface:
    surface_id: str
    authority_class: str
    entrypoint: str
    accepted_artifacts: List[str]
    emitted_artifacts: List[str]
    notes: str


RUNTIME_SURFACES: Dict[str, RuntimeSurface] = {
    "runtime.cli": RuntimeSurface(
        surface_id="runtime.cli",
        authority_class="runtime_control",
        entrypoint="AI_GO/core/runtime/cli.py",
        accepted_artifacts=["command_request"],
        emitted_artifacts=["runtime_command_result"],
        notes="Primary runtime command surface.",
    ),
    "runtime.router": RuntimeSurface(
        surface_id="runtime.router",
        authority_class="routing_control",
        entrypoint="AI_GO/core/runtime/router.py",
        accepted_artifacts=[
            "screened_research_packet",
            "arbitration_decision_packet",
            "pm_intake_record",
            "pm_continuity_update",
        ],
        emitted_artifacts=[
            "routing_decision",
            "runtime_route_receipt",
        ],
        notes="Bounded runtime router for governed layer-to-layer handoff.",
    ),
    "engines.refinement_arbitrator": RuntimeSurface(
        surface_id="engines.refinement_arbitrator",
        authority_class="refinement_governance",
        entrypoint="AI_GO/engines/refinement_arbitrator/engine.py:run_arbitration",
        accepted_artifacts=["screened_research_packet"],
        emitted_artifacts=[
            "arbitration_decision_packet",
            "arbitration_receipt",
        ],
        notes="Stage 16 propagation-governance surface for screened research packets.",
    ),
    "pm.refinement.arbitration_intake": RuntimeSurface(
        surface_id="pm.refinement.arbitration_intake",
        authority_class="pm_intake",
        entrypoint="AI_GO/PM_CORE/refinement/arbitration_intake.py:intake_arbitration_decision",
        accepted_artifacts=["arbitration_decision_packet"],
        emitted_artifacts=[
            "pm_intake_record",
            "pm_intake_receipt",
        ],
        notes="PM-facing intake surface for arbitration decision packets.",
    ),
    "pm.smi.continuity": RuntimeSurface(
        surface_id="pm.smi.continuity",
        authority_class="pm_decision_memory",
        entrypoint="AI_GO/PM_CORE/smi/pm_continuity.py:update_pm_continuity",
        accepted_artifacts=["pm_intake_record"],
        emitted_artifacts=[
            "pm_continuity_update",
            "pm_continuity_receipt",
        ],
        notes="Stage 17 PM-owned decision-memory surface for PM intake continuity updates.",
    ),
    "pm.strategy": RuntimeSurface(
        surface_id="pm.strategy",
        authority_class="pm_decision",
        entrypoint="AI_GO/PM_CORE/strategy/pm_strategy.py:run_pm_strategy",
        accepted_artifacts=["pm_continuity_update"],
        emitted_artifacts=[
            "pm_decision_packet",
            "pm_strategy_receipt",
        ],
        notes="Stage 18 PM strategic decision surface for consolidating continuity into downstream decision packets.",
    ),
}


def get_runtime_surface(surface_id: str) -> RuntimeSurface:
    if surface_id not in RUNTIME_SURFACES:
        raise KeyError(f"Unknown runtime surface: {surface_id}")
    return RUNTIME_SURFACES[surface_id]


def list_runtime_surfaces() -> List[str]:
    return sorted(RUNTIME_SURFACES.keys())
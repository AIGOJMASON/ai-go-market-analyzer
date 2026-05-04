from __future__ import annotations

from typing import Dict, Any

from .pm_refinement import PMRefinement
from .reasoning_refinement import ReasoningRefinement
from .narrative_refinement import NarrativeRefinement


class RefinementGate:
    """
    Coordinates the refinement process across multiple refinement perspectives.
    """

    def __init__(self) -> None:
        self.pm_refiner = PMRefinement()
        self.reasoning_refiner = ReasoningRefinement()
        self.narrative_refiner = NarrativeRefinement()

    def refine_research_packet(self, research_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run refinement across the three refinement domains.
        """

        pm_surface = self.pm_refiner.refine(research_packet)
        reasoning_surface = self.reasoning_refiner.refine(research_packet)
        narrative_surface = self.narrative_refiner.refine(research_packet)

        return {
            "refinement_status": "complete",
            "pm_surface": pm_surface,
            "reasoning_surface": reasoning_surface,
            "narrative_surface": narrative_surface,
        }
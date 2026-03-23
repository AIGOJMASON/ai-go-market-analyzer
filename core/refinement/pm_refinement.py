from __future__ import annotations

from typing import Dict, Any


class PMRefinement:
    """
    Strategic interpretation surface.

    Produces strategic signals from research context without making
    planning decisions.
    """

    def refine(self, research_packet: Dict[str, Any]) -> Dict[str, Any]:

        return {
            "layer": "pm_refinement",
            "strategic_summary": research_packet.get("summary"),
            "signal_type": research_packet.get("signal_type"),
            "status": "interpreted",
        }
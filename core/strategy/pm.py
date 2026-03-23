from __future__ import annotations

from typing import Dict, Any


class PMCoreService:
    """
    Strategic interpretation surface.

    Converts refinement bundles into strategic planning signals.
    """

    def interpret_refinement_bundle(self, refinement_bundle: Dict[str, Any]) -> Dict[str, Any]:

        pm_surface = refinement_bundle.get("pm_surface", {})

        return {
            "strategy_status": "interpreted",
            "signal_type": pm_surface.get("signal_type"),
            "strategic_summary": pm_surface.get("strategic_summary"),
        }
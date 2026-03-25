from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.api.pm_influence import build_pm_influence_record
    from AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner import run_live_case
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
except ModuleNotFoundError:
    from api.pm_influence import build_pm_influence_record
    from child_cores.market_analyzer_v1.ui.live_data_runner import run_live_case
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )


def _coerce_refinement_packet(result: Dict[str, Any]) -> Dict[str, Any] | None:
    refinement_packet = result.get("refinement_packet")
    if isinstance(refinement_packet, dict):
        return refinement_packet

    refinement_panel = result.get("refinement_panel")
    if isinstance(refinement_panel, dict):
        return refinement_panel

    cognition_panel = result.get("cognition_panel")
    if isinstance(cognition_panel, dict):
        refinement = cognition_panel.get("refinement")
        if isinstance(refinement, dict):
            return refinement

    return None


def _apply_pm_influence(result: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(result)

    refinement_packet = _coerce_refinement_packet(enriched)
    if not refinement_packet:
        enriched["pm_influence_record"] = build_pm_influence_record(None)
        return enriched

    enriched["pm_influence_record"] = build_pm_influence_record(refinement_packet)
    return enriched


def run_operator_dashboard(case_id: str) -> Dict[str, Any]:
    """
    Canonical operator-facing dashboard runner for Market Analyzer V1.

    Flow:
    1. execute the governed live-style case runner
    2. derive bounded PM influence from refinement output
    3. build stable operator dashboard payload
    """
    result = run_live_case(case_id)
    influenced_result = _apply_pm_influence(result)
    dashboard = build_operator_dashboard(influenced_result)

    return {
        "status": "ok",
        "case_id": case_id,
        "dashboard": dashboard,
    }

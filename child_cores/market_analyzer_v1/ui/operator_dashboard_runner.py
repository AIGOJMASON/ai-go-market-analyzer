from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from api.pm_influence import build_pm_influence_record
    from child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )
except ModuleNotFoundError:
    from AI_GO.api.pm_influence import build_pm_influence_record
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder import (
        build_operator_dashboard,
    )


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def run_operator_dashboard(
    routed_result: Dict[str, Any],
    refinement_packets: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Lawful Phase 6 runner.

    This function expects a routed_result that already came from the PM-owned
    strategy/output surface. It then attaches bounded refinement influence
    before building the final operator-visible dashboard.

    Important:
    - PM still owns recommendation generation
    - refinement only contributes bounded influence
    - output remains advisory-only
    """
    result = _safe_dict(routed_result)
    core_id = result.get("core_id", "market_analyzer_v1")

    if refinement_packets is None:
        refinement_packets = _safe_list(result.get("refinement_packets"))

    pm_influence_record = build_pm_influence_record(
        core_id=core_id,
        recommendation_panel=result.get("recommendation_panel"),
        refinement_packets=refinement_packets,
    )

    return build_operator_dashboard(
        routed_result=result,
        pm_influence_record=pm_influence_record,
    )
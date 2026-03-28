from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response
except ModuleNotFoundError:
    from api.schemas.market_analyzer_response import build_market_analyzer_response


def build_operator_dashboard(result: Dict[str, Any]) -> Dict[str, Any]:
    response_model = build_market_analyzer_response(result)
    response = response_model.model_dump(by_alias=True, exclude_none=False)

    system_view = response.get("system_view", {}) or {}

    case_view = system_view.get("case", {})
    runtime_view = system_view.get("runtime", {})
    recommendation_view = system_view.get("recommendation", {})
    cognition_view = system_view.get("cognition", {})
    pm_view = system_view.get("pm_workflow", {})
    governance_view = system_view.get("governance", {})

    return {
        "status": response.get("status", "ok"),
        "request_id": response.get("request_id"),
        "core_id": response.get("core_id", "market_analyzer_v1"),
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "route_mode": response.get("route_mode"),
        "mode": response.get("mode", "advisory"),
        "execution_allowed": response.get("execution_allowed", False),

        # projection surfaces
        "case_panel": response.get("case_panel") or case_view,
        "runtime_panel": response.get("runtime_panel") or runtime_view,
        "recommendation_panel": response.get("recommendation_panel") or recommendation_view,
        "cognition_panel": response.get("cognition_panel") or cognition_view,
        "pm_workflow_panel": response.get("pm_workflow_panel") or pm_view,
        "governance_panel": response.get("governance_panel") or governance_view,

        "rejection_panel": response.get("rejection_panel"),
        "refinement_panel": response.get("refinement_panel"),

        # live external-memory pattern visibility
        "external_memory_pattern_panel": result.get("external_memory_pattern_panel"),

        "pm_influence_record": result.get("pm_influence_record"),
        "system_view": system_view,
    }
from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response
except ModuleNotFoundError:
    from api.schemas.market_analyzer_response import build_market_analyzer_response


def build_operator_dashboard(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert governed runtime / live-run output into the stable operator dashboard payload.

    This keeps the canonical outward contract centered on the response builder while
    allowing the operator runner to inject bounded PM influence before rendering.
    """
    response_model = build_market_analyzer_response(result)
    response = response_model.model_dump(by_alias=True, exclude_none=False)

    system_view = response.get("system_view", {})

    return {
        "status": response.get("status", "ok"),
        "request_id": response.get("request_id"),
        "core_id": response.get("core_id", "market_analyzer_v1"),
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "route_mode": response.get("route_mode"),
        "mode": response.get("mode", "advisory"),
        "execution_allowed": response.get("execution_allowed", False),
        "case_panel": response.get("case_panel", {}),
        "runtime_panel": response.get("runtime_panel", response.get("market_panel", {})),
        "recommendation_panel": response.get("recommendation_panel", {}),
        "cognition_panel": response.get("cognition_panel", response.get("refinement_panel", {})),
        "pm_workflow_panel": response.get("pm_workflow_panel", {}),
        "governance_panel": response.get("governance_panel", {}),
        "rejection_panel": response.get("rejection_panel"),
        "refinement_panel": response.get("refinement_panel"),
        "pm_influence_record": result.get("pm_influence_record"),
        "system_view": system_view,
    }

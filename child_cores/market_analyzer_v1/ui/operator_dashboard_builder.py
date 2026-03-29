from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response
except ModuleNotFoundError:
    from api.schemas.market_analyzer_response import build_market_analyzer_response


def build_operator_dashboard(result: Dict[str, Any]) -> Dict[str, Any]:
    response = build_market_analyzer_response(result)

    case_view = response.get("case_panel", {}) or {}
    market_view = response.get("market_panel", {}) or {}
    runtime_view = response.get("runtime_panel", {}) or {}
    recommendation_view = response.get("recommendation_panel", {}) or {}
    cognition_view = response.get("cognition_panel", {}) or response.get("refinement_panel", {}) or {}
    pm_view = response.get("pm_workflow_panel", {}) or {}
    governance_view = response.get("governance_panel", {}) or {}

    return {
        "status": response.get("status", "ok"),
        "request_id": response.get("request_id"),
        "core_id": response.get("core_id", "market_analyzer_v1"),
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "route_mode": response.get("route_mode"),
        "mode": response.get("mode", "advisory"),
        "execution_allowed": response.get("execution_allowed", False),
        "approval_required": response.get("approval_required", True),

        "case_panel": case_view,
        "market_panel": market_view,
        "runtime_panel": runtime_view,
        "recommendation_panel": recommendation_view,
        "cognition_panel": cognition_view,
        "refinement_panel": response.get("refinement_panel") or cognition_view,
        "pm_workflow_panel": pm_view,
        "governance_panel": governance_view,

        "rejection_panel": response.get("rejection_panel"),
        "external_memory_panel": response.get("external_memory_panel"),
        "pre_interface_watcher": response.get("pre_interface_watcher"),
        "pre_interface_smi": response.get("pre_interface_smi"),

        "external_memory_runtime_result": result.get("external_memory_runtime_result"),
        "external_memory_retrieval_artifact": result.get("external_memory_retrieval_artifact"),
        "external_memory_retrieval_receipt": result.get("external_memory_retrieval_receipt"),
        "external_memory_promotion_artifact": result.get("external_memory_promotion_artifact"),
        "external_memory_promotion_receipt": result.get("external_memory_promotion_receipt"),
        "external_memory_pattern_panel": result.get("external_memory_pattern_panel"),
        "pm_influence_record": result.get("pm_influence_record"),
    }

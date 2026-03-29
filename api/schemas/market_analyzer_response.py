# AI_GO/api/schemas/market_analyzer_response.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenericPanel(BaseModel):
    model_config = {
        "extra": "allow",
    }


class MarketAnalyzerResponse(BaseModel):
    status: str
    request_id: Optional[str] = None
    core_id: str = "market_analyzer_v1"
    route_mode: Optional[str] = None
    mode: str = "advisory"
    execution_allowed: bool = False
    approval_required: Optional[bool] = None
    dashboard_type: str = "market_analyzer_v1_operator_dashboard"

    case_panel: Optional[GenericPanel] = None
    market_panel: Optional[GenericPanel] = None
    runtime_panel: Optional[GenericPanel] = None
    candidate_panel: Optional[GenericPanel] = None
    recommendation_panel: Optional[GenericPanel] = None
    governance_panel: Optional[GenericPanel] = None
    rejection_panel: Optional[GenericPanel] = None
    refinement_panel: Optional[GenericPanel] = None
    external_memory_panel: Optional[GenericPanel] = None
    pm_workflow_panel: Optional[GenericPanel] = None

    pre_interface_watcher: Optional[GenericPanel] = None
    pre_interface_smi: Optional[GenericPanel] = None

    model_config = {
        "extra": "allow",
    }


def build_market_analyzer_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    return MarketAnalyzerResponse(**payload).model_dump(exclude_none=True)


def build_market_analyzer_response_list(payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [build_market_analyzer_response(payload) for payload in payloads]

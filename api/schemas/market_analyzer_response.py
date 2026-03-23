from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CasePanel(BaseModel):
    case_id: str
    title: str
    observed_at: str


class MarketPanel(BaseModel):
    market_regime: str
    event_theme: str
    macro_bias: str
    headline: str


class CandidatePanel(BaseModel):
    candidate_count: int
    symbols: List[str]


class RecommendationItem(BaseModel):
    symbol: str
    entry: str
    exit: str
    confidence: str


class RecommendationPanel(BaseModel):
    recommendation_count: int
    recommendations: List[RecommendationItem]


class GovernancePanel(BaseModel):
    watcher_passed: bool
    approval_required: bool
    execution_allowed: bool
    approval_gate: str
    receipt_id: str


class RejectionPanel(BaseModel):
    rejected: bool
    reason: Optional[str] = None


class MarketAnalyzerResponse(BaseModel):
    status: str = Field(description="API call status.")
    request_id: Optional[str] = Field(
        default=None,
        description="Optional caller-supplied request identifier.",
    )
    core_id: str
    dashboard_type: str
    route_mode: str
    mode: str
    execution_allowed: bool
    case_panel: CasePanel
    market_panel: MarketPanel
    candidate_panel: CandidatePanel
    recommendation_panel: RecommendationPanel
    governance_panel: GovernancePanel
    rejection_panel: RejectionPanel


def build_market_analyzer_response(
    dashboard: dict,
    request_id: Optional[str] = None,
) -> MarketAnalyzerResponse:
    return MarketAnalyzerResponse(
        status="ok",
        request_id=request_id,
        core_id=dashboard["core_id"],
        dashboard_type=dashboard["dashboard_type"],
        route_mode=dashboard["route_mode"],
        mode="advisory",
        execution_allowed=bool(dashboard["governance_panel"]["execution_allowed"]),
        case_panel=CasePanel(**dashboard["case_panel"]),
        market_panel=MarketPanel(**dashboard["market_panel"]),
        candidate_panel=CandidatePanel(**dashboard["candidate_panel"]),
        recommendation_panel=RecommendationPanel(**dashboard["recommendation_panel"]),
        governance_panel=GovernancePanel(**dashboard["governance_panel"]),
        rejection_panel=RejectionPanel(**dashboard["rejection_panel"]),
    )
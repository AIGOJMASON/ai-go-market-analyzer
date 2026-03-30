from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CasePanel(BaseModel):
    case_id: Optional[str] = None
    title: Optional[str] = None
    observed_at: Optional[str] = None
    input_mode: Optional[str] = None


class RuntimeCandidate(BaseModel):
    symbol: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None


class RuntimePanel(BaseModel):
    market_regime: Optional[str] = None
    event_theme: Optional[str] = None
    macro_bias: Optional[str] = None
    headline: Optional[str] = None
    candidate_count: int = 0
    candidates: List[Dict[str, Any]] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    symbol: Optional[str] = None
    entry: Optional[str] = None
    exit: Optional[str] = None
    confidence: Optional[str] = None
    thesis: Optional[str] = None


class RecommendationPanel(BaseModel):
    state: str = "empty"
    count: int = 0
    items: List[Dict[str, Any]] = Field(default_factory=list)


class GovernancePanel(BaseModel):
    mode: str = "advisory"
    execution_allowed: bool = False
    approval_required: bool = True
    watcher_passed: Optional[bool] = None
    watcher_status: Optional[str] = None
    closeout_status: Optional[str] = None
    requires_review: bool = False
    receipt_id: Optional[str] = None
    watcher_validation_id: Optional[str] = None
    closeout_id: Optional[str] = None


class RejectionPanel(BaseModel):
    status: str = "rejected"
    reason: Optional[str] = None
    detail: Optional[str] = None
    rejection_class: Optional[str] = None


class RefinementPanel(BaseModel):
    visible: bool = True
    signal: Optional[str] = None
    confidence_adjustment: Optional[str] = None
    risk_flag: Optional[str] = None
    insight: Optional[str] = None
    narrative: Optional[str] = None
    source: str = "stage16_refinement_arbitrator"


class PMWorkflowSubpanel(BaseModel):
    summary: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    target: Optional[str] = None
    record_id: Optional[str] = None


class PMWorkflowPanel(BaseModel):
    strategy: Dict[str, Any] = Field(default_factory=dict)
    review: Dict[str, Any] = Field(default_factory=dict)
    plan: Dict[str, Any] = Field(default_factory=dict)
    queue: Dict[str, Any] = Field(default_factory=dict)
    dispatch: Dict[str, Any] = Field(default_factory=dict)


class ExternalMemorySimilarEvent(BaseModel):
    event_id: Optional[str] = None
    symbol: Optional[str] = None
    event_theme: Optional[str] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None


class ExternalMemoryPanel(BaseModel):
    visible: bool = True
    source: str = "external_memory"
    advisory_only: bool = True
    pattern_detected: bool = False
    pattern_strength: Optional[str] = None
    historical_confirmation: Optional[str] = None
    confidence_adjustment: Optional[str] = None
    summary: Optional[str] = None
    dominant_symbol: Optional[str] = None
    dominant_sector: Optional[str] = None
    recurrence_count: int = 0
    temporal_span_days: int = 0
    similar_events: List[Dict[str, Any]] = Field(default_factory=list)
    provenance_refs: List[Any] = Field(default_factory=list)


class PreInterfaceWatcher(BaseModel):
    status: Optional[str] = None
    reason: Optional[str] = None
    watcher_receipt_id: Optional[str] = None


class PreInterfaceSMI(BaseModel):
    recommendation_count: Optional[int] = None
    exposure_posture: Optional[str] = None
    visible_panels: List[str] = Field(default_factory=list)
    refinement_visible: Optional[bool] = None
    external_memory_visible: Optional[bool] = None


class MarketAnalyzerResponse(BaseModel):
    status: str = "ok"
    request_id: Optional[str] = None
    core_id: str = "market_analyzer_v1"
    route_mode: Optional[str] = None
    mode: str = "advisory"
    execution_allowed: bool = False

    case_panel: CasePanel
    runtime_panel: RuntimePanel
    recommendation_panel: RecommendationPanel
    governance_panel: GovernancePanel

    rejection_panel: Optional[RejectionPanel] = None
    refinement_panel: Optional[RefinementPanel] = None
    pm_workflow_panel: Optional[PMWorkflowPanel] = None
    external_memory_panel: Optional[ExternalMemoryPanel] = None

    pre_interface_watcher: Optional[PreInterfaceWatcher] = None
    pre_interface_smi: Optional[PreInterfaceSMI] = None


def build_market_analyzer_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Canonical outward response serializer.

    Keeps the single-surface contract stable while allowing optional panels such
    as refinement and external memory to appear only when present and dict-shaped.
    """
    model = MarketAnalyzerResponse(**payload)
    return model.model_dump(exclude_none=True)
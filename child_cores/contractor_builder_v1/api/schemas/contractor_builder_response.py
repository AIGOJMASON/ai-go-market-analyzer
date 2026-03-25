from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


ResponseStatus = Literal["ok", "rejected", "error"]
RecommendationState = Literal["present", "none", "rejected"]
NodeState = Literal["present", "none"]
ConfidenceAdjustment = Literal["up", "down", "none"]
InputMode = Literal["fixture", "live"]


class RecommendationItem(BaseModel):
    package_id: str
    title: str
    rationale: Optional[str] = None
    confidence: Optional[str] = None


class CasePanel(BaseModel):
    case_id: str
    title: str
    observed_at: Optional[str] = None
    input_mode: InputMode = "fixture"


class RuntimePanel(BaseModel):
    project_class: Optional[str] = None
    trade_profile: Optional[str] = None
    complexity_level: Optional[str] = None
    location_mode: Optional[str] = None
    scope_summary: Optional[str] = None
    candidate_count: int = 0
    candidates: List[str] = Field(default_factory=list)


class RecommendationPanel(BaseModel):
    state: RecommendationState = "none"
    count: int = 0
    items: List[RecommendationItem] = Field(default_factory=list)
    summary: str = "No package recommendation issued."


class RefinementPanel(BaseModel):
    state: NodeState = "none"
    signal: Optional[str] = None
    confidence_adjustment: Optional[ConfidenceAdjustment] = None
    risk_flag: Optional[str] = None
    insight: Optional[str] = None
    narrative: Optional[str] = None


class CognitionPanel(BaseModel):
    refinement: RefinementPanel = Field(default_factory=RefinementPanel)


class PMWorkflowStrategy(BaseModel):
    class_name: Optional[str] = Field(default=None, alias="class")
    strength: Optional[str] = None
    trend: Optional[str] = None
    posture: Optional[str] = None

    model_config = {"populate_by_name": True}


class PMWorkflowReview(BaseModel):
    class_name: Optional[str] = Field(default=None, alias="class")
    priority: Optional[str] = None

    model_config = {"populate_by_name": True}


class PMWorkflowPlan(BaseModel):
    class_name: Optional[str] = Field(default=None, alias="class")
    next_step: Optional[str] = None
    priority: Optional[str] = None

    model_config = {"populate_by_name": True}


class PMWorkflowQueue(BaseModel):
    lane: Optional[str] = None
    status: Optional[str] = None
    target: Optional[str] = None
    priority: Optional[str] = None


class PMWorkflowDispatch(BaseModel):
    class_name: Optional[str] = Field(default=None, alias="class")
    target: Optional[str] = None
    status: Optional[str] = None
    ready: bool = False

    model_config = {"populate_by_name": True}


class PMWorkflowPanel(BaseModel):
    state: NodeState = "none"
    strategy: PMWorkflowStrategy = Field(default_factory=PMWorkflowStrategy)
    review: PMWorkflowReview = Field(default_factory=PMWorkflowReview)
    plan: PMWorkflowPlan = Field(default_factory=PMWorkflowPlan)
    queue: PMWorkflowQueue = Field(default_factory=PMWorkflowQueue)
    dispatch: PMWorkflowDispatch = Field(default_factory=PMWorkflowDispatch)


class GovernancePanel(BaseModel):
    mode: str = "advisory"
    route_mode: Optional[str] = None
    execution_allowed: bool = False
    approval_required: bool = True
    watcher_passed: Optional[bool] = None
    closeout_status: Optional[str] = None
    receipt_id: Optional[str] = None
    watcher_validation_id: Optional[str] = None
    closeout_id: Optional[str] = None
    requires_review: bool = False


class SystemView(BaseModel):
    case: CasePanel
    runtime: RuntimePanel
    recommendation: RecommendationPanel
    cognition: CognitionPanel = Field(default_factory=CognitionPanel)
    pm_workflow: PMWorkflowPanel = Field(default_factory=PMWorkflowPanel)
    governance: GovernancePanel = Field(default_factory=GovernancePanel)


class ContractorBuilderResponse(BaseModel):
    status: ResponseStatus
    request_id: str
    system_view: SystemView


def _safe_get(source: Optional[dict[str, Any]], key: str, default: Any = None) -> Any:
    if not isinstance(source, dict):
        return default
    return source.get(key, default)


def _resolve_input_mode(payload: dict[str, Any]) -> InputMode:
    explicit_input_mode = str(payload.get("input_mode", "")).strip().lower()
    route_mode = str(payload.get("route_mode", "")).strip().lower()

    if explicit_input_mode == "live":
        return "live"
    if "live" in route_mode:
        return "live"
    return "fixture"


def _build_recommendation_panel(payload: dict[str, Any]) -> RecommendationPanel:
    recommendation_panel = _safe_get(payload, "recommendation_panel", {}) or {}
    raw_items = recommendation_panel.get("recommendations", []) or []

    items = [
        RecommendationItem(
            package_id=item.get("package_id", ""),
            title=item.get("title", ""),
            rationale=item.get("rationale"),
            confidence=item.get("confidence"),
        )
        for item in raw_items
        if isinstance(item, dict)
    ]

    if items:
        state = "present"
        summary = f"{len(items)} package recommendation(s) issued."
    else:
        rejection_panel = _safe_get(payload, "rejection_panel", {}) or {}
        state = "rejected" if rejection_panel else "none"
        summary = rejection_panel.get("reason", "No package recommendation issued.")

    return RecommendationPanel(
        state=state,
        count=len(items),
        items=items,
        summary=summary,
    )


def _build_refinement_panel(payload: dict[str, Any]) -> RefinementPanel:
    refinement = (
        _safe_get(payload, "refinement_panel")
        or _safe_get(payload, "refinement")
        or _safe_get(payload, "refinement_packet")
        or {}
    )

    if not refinement:
        return RefinementPanel(state="none")

    confidence_adjustment = refinement.get("confidence_adjustment")
    if confidence_adjustment not in {"up", "down", "none", None}:
        confidence_adjustment = "none"

    return RefinementPanel(
        state="present",
        signal=refinement.get("signal"),
        confidence_adjustment=confidence_adjustment,
        risk_flag=refinement.get("risk_flag"),
        insight=refinement.get("insight"),
        narrative=refinement.get("narrative"),
    )


def _build_pm_workflow_panel(payload: dict[str, Any]) -> PMWorkflowPanel:
    strategy = _safe_get(payload, "pm_strategy_record", {}) or {}
    review = _safe_get(payload, "pm_review_record", {}) or {}
    plan = _safe_get(payload, "pm_planning_record", {}) or {}
    queue = _safe_get(payload, "pm_queue_record", {}) or {}
    dispatch = _safe_get(payload, "pm_workflow_dispatch_record", {}) or {}

    has_any = any([strategy, review, plan, queue, dispatch])
    if not has_any:
        return PMWorkflowPanel(state="none")

    return PMWorkflowPanel(
        state="present",
        strategy=PMWorkflowStrategy(
            **{
                "class": strategy.get("strategy_class") or strategy.get("class"),
                "strength": strategy.get("continuity_strength") or strategy.get("strength"),
                "trend": strategy.get("trend_direction") or strategy.get("trend"),
                "posture": strategy.get("posture"),
            }
        ),
        review=PMWorkflowReview(
            **{
                "class": review.get("review_class") or review.get("class"),
                "priority": review.get("review_priority") or review.get("priority"),
            }
        ),
        plan=PMWorkflowPlan(
            **{
                "class": plan.get("plan_class") or plan.get("class"),
                "next_step": plan.get("next_step_class") or plan.get("next_step"),
                "priority": plan.get("plan_priority") or plan.get("priority"),
            }
        ),
        queue=PMWorkflowQueue(
            lane=queue.get("queue_lane") or queue.get("lane"),
            status=queue.get("queue_status") or queue.get("status"),
            target=queue.get("queue_target") or queue.get("target"),
            priority=queue.get("queue_priority") or queue.get("priority"),
        ),
        dispatch=PMWorkflowDispatch(
            **{
                "class": dispatch.get("dispatch_class") or dispatch.get("class"),
                "target": dispatch.get("dispatch_target") or dispatch.get("target"),
                "status": dispatch.get("dispatch_status") or dispatch.get("status"),
                "ready": bool(
                    dispatch.get("dispatch_ready")
                    if "dispatch_ready" in dispatch
                    else dispatch.get("ready", False)
                ),
            }
        ),
    )


def build_contractor_builder_response(payload: dict[str, Any]) -> ContractorBuilderResponse:
    case_panel = _safe_get(payload, "case_panel", {}) or {}
    runtime_panel = _safe_get(payload, "runtime_panel", {}) or {}
    governance_panel = _safe_get(payload, "governance_panel", {}) or {}

    response = ContractorBuilderResponse(
        status=payload.get("status", "ok"),
        request_id=payload.get("request_id", ""),
        system_view=SystemView(
            case=CasePanel(
                case_id=case_panel.get("case_id", payload.get("request_id", "")),
                title=case_panel.get("title", ""),
                observed_at=case_panel.get("observed_at"),
                input_mode=_resolve_input_mode(payload),
            ),
            runtime=RuntimePanel(
                project_class=runtime_panel.get("project_class"),
                trade_profile=runtime_panel.get("trade_profile"),
                complexity_level=runtime_panel.get("complexity_level"),
                location_mode=runtime_panel.get("location_mode"),
                scope_summary=runtime_panel.get("scope_summary"),
                candidate_count=runtime_panel.get("candidate_count", 0),
                candidates=runtime_panel.get("candidates", []) or [],
            ),
            recommendation=_build_recommendation_panel(payload),
            cognition=CognitionPanel(refinement=_build_refinement_panel(payload)),
            pm_workflow=_build_pm_workflow_panel(payload),
            governance=GovernancePanel(
                mode=payload.get("mode", "advisory"),
                route_mode=payload.get("route_mode"),
                execution_allowed=bool(payload.get("execution_allowed", False)),
                approval_required=bool(payload.get("approval_required", True)),
                watcher_passed=governance_panel.get("watcher_passed", payload.get("watcher_passed")),
                closeout_status=payload.get("closeout_status"),
                receipt_id=payload.get("receipt_id"),
                watcher_validation_id=payload.get("watcher_validation_id"),
                closeout_id=payload.get("closeout_id"),
                requires_review=bool(payload.get("requires_review", False)),
            ),
        ),
    )
    return response
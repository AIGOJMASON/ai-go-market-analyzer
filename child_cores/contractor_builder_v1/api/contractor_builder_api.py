from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from AI_GO.child_cores.contractor_builder_v1.api.schemas.contractor_builder_request import (
    ContractorBuilderFixtureRequest,
    ContractorBuilderLiveRequest,
)
from AI_GO.child_cores.contractor_builder_v1.api.schemas.contractor_builder_response import (
    build_contractor_builder_response,
)

router = APIRouter(prefix="/contractor-builder", tags=["contractor-builder-v1"])


def _run_contractor_builder_logic(request_payload: Dict[str, Any]) -> Dict[str, Any]:
    request_id = request_payload.get("request_id", "contractor-001")
    scope_summary = request_payload.get("scope_summary", "Fixture planning case")
    project_type = request_payload.get("project_type", "remodel")
    trade_focus = request_payload.get("trade_focus", "general")
    budget_band = request_payload.get("budget_band", "medium")
    timeline_band = request_payload.get("timeline_band", "near_term")
    location_mode = request_payload.get("location_mode", "remote")
    confirmation = request_payload.get("confirmation", "partial")
    force_rejection = bool(request_payload.get("force_rejection", False))

    is_live = "project_type" in request_payload
    route_mode = "pm_route_live" if is_live else "pm_route"
    input_mode = "live" if is_live else "fixture"

    if force_rejection or confirmation == "missing":
        return {
            "status": "ok",
            "request_id": request_id,
            "route_mode": route_mode,
            "input_mode": input_mode,
            "mode": "advisory",
            "execution_allowed": False,
            "approval_required": True,
            "receipt_id": f"rcpt_{request_id}",
            "watcher_validation_id": f"watcher_{request_id}",
            "closeout_id": f"closeout_{request_id}",
            "closeout_status": "accepted",
            "requires_review": False,
            "governance_panel": {
                "watcher_passed": True,
            },
            "case_panel": {
                "case_id": request_id,
                "title": scope_summary,
                "observed_at": None,
            },
            "runtime_panel": {
                "project_class": project_type,
                "trade_profile": trade_focus,
                "complexity_level": "medium",
                "location_mode": location_mode,
                "scope_summary": scope_summary,
                "candidate_count": 0,
                "candidates": [],
            },
            "recommendation_panel": {
                "recommendations": [],
            },
            "rejection_panel": {
                "reason": "insufficient confirmation for package recommendation",
            },
            "refinement_panel": {
                "signal": "confirmation_gap_detected",
                "confidence_adjustment": "down",
                "risk_flag": "missing_confirmation",
                "insight": "Scope needs stronger confirmation before package recommendation.",
                "narrative": "Workflow remains advisory and non-executing.",
            },
            "pm_strategy_record": {
                "strategy_class": "elevated_caution",
                "continuity_strength": "medium",
                "trend_direction": "flat",
                "posture": "monitor",
            },
            "pm_review_record": {
                "review_class": "review",
                "review_priority": "medium",
            },
            "pm_planning_record": {
                "plan_class": "prepare_review",
                "next_step_class": "prepare_review",
                "plan_priority": "medium",
            },
            "pm_queue_record": {
                "queue_lane": "review",
                "queue_status": "queued",
                "queue_target": "pm",
                "queue_priority": "medium",
            },
            "pm_workflow_dispatch_record": {
                "dispatch_class": "review_dispatch",
                "dispatch_target": "pm_review",
                "dispatch_status": "ready",
                "dispatch_ready": True,
            },
        }

    return {
        "status": "ok",
        "request_id": request_id,
        "route_mode": route_mode,
        "input_mode": input_mode,
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "receipt_id": f"rcpt_{request_id}",
        "watcher_validation_id": f"watcher_{request_id}",
        "closeout_id": f"closeout_{request_id}",
        "closeout_status": "accepted",
        "requires_review": False,
        "governance_panel": {
            "watcher_passed": True,
        },
        "case_panel": {
            "case_id": request_id,
            "title": scope_summary,
            "observed_at": None,
        },
        "runtime_panel": {
            "project_class": project_type,
            "trade_profile": trade_focus,
            "complexity_level": "medium" if budget_band != "low" else "low",
            "location_mode": location_mode,
            "scope_summary": scope_summary,
            "candidate_count": 1,
            "candidates": [f"{trade_focus}_package_v1"],
        },
        "recommendation_panel": {
            "recommendations": [
                {
                    "package_id": f"{trade_focus}_package_v1",
                    "title": f"{trade_focus.title()} Planning Package",
                    "rationale": f"Aligned to {project_type} scope with {timeline_band} timeline.",
                    "confidence": "medium",
                }
            ],
        },
        "refinement_panel": {
            "signal": "scope_alignment_confirmed",
            "confidence_adjustment": "none",
            "risk_flag": None,
            "insight": "Scope, trade, and timeline support a planning package recommendation.",
            "narrative": "Governed output remains advisory and non-executing.",
        },
        "pm_strategy_record": {
            "strategy_class": "reinforced_support",
            "continuity_strength": "medium",
            "trend_direction": "up",
            "posture": "supportive",
        },
        "pm_review_record": {
            "review_class": "plan",
            "review_priority": "medium",
        },
        "pm_planning_record": {
            "plan_class": "prepare_plan",
            "next_step_class": "prepare_plan",
            "plan_priority": "medium",
        },
        "pm_queue_record": {
            "queue_lane": "planning",
            "queue_status": "queued",
            "queue_target": "pm",
            "queue_priority": "medium",
        },
        "pm_workflow_dispatch_record": {
            "dispatch_class": "planning_dispatch",
            "dispatch_target": "pm_planning",
            "dispatch_status": "ready",
            "dispatch_ready": True,
        },
    }


@router.post("/run")
def run_contractor_builder(request_payload: ContractorBuilderFixtureRequest) -> Dict[str, Any]:
    raw_payload = _run_contractor_builder_logic(request_payload.model_dump())
    response = build_contractor_builder_response(raw_payload)
    return response.model_dump(by_alias=True, exclude_none=False)


@router.post("/run/live")
def run_contractor_builder_live(request_payload: ContractorBuilderLiveRequest) -> Dict[str, Any]:
    raw_payload = _run_contractor_builder_logic(request_payload.model_dump())
    response = build_contractor_builder_response(raw_payload)
    return response.model_dump(by_alias=True, exclude_none=False)
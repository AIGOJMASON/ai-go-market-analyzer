"""
Risk API surface for contractor_builder_v1 (governed).
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_service import (
    create_risk,
    review_risk,
    transition_risk,
)

router = APIRouter(prefix="/risk", tags=["contractor_risk"])


class RiskCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]
    actor: str = "contractor_risk_api"


class RiskTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str
    notes: str = ""
    actor: str = "contractor_risk_api"


class RiskReviewRequest(BaseModel):
    entry: Dict[str, Any]
    reviewer_name: str
    reviewer_role: str
    notes: str = ""
    actor: str = "contractor_risk_api"


@router.post("/create")
def create_risk_entry(request: RiskCreateRequest) -> Dict[str, Any]:
    try:
        return create_risk(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/review")
def review_risk_entry(request: RiskReviewRequest) -> Dict[str, Any]:
    try:
        return review_risk(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_risk_entry(request: RiskTransitionRequest) -> Dict[str, Any]:
    try:
        return transition_risk(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
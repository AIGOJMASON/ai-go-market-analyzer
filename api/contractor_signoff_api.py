from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.signoff.signoff_service import (
    check_signoff_complete,
    check_signoff_decline,
    complete_signoff,
    decline_signoff,
)


router = APIRouter(prefix="/signoff", tags=["contractor_signoff"])


class SignoffRequest(BaseModel):
    project_id: str
    phase_id: str
    actor: str = "contractor_signoff_api"


@router.post("/complete/check")
def check_complete_signoff_route(request: SignoffRequest) -> Dict[str, Any]:
    try:
        return check_signoff_complete(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/complete")
def complete_signoff_route(request: SignoffRequest) -> Dict[str, Any]:
    try:
        return complete_signoff(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/decline/check")
def check_decline_signoff_route(request: SignoffRequest) -> Dict[str, Any]:
    try:
        return check_signoff_decline(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/decline")
def decline_signoff_route(request: SignoffRequest) -> Dict[str, Any]:
    try:
        return decline_signoff(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
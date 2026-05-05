from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.core.state_runtime.state_authority import (
    build_state_authority_packet,
    summarize_state_authority,
)


router = APIRouter(prefix="/state-authority", tags=["contractor_state_authority"])


class StateAuthorityCheckRequest(BaseModel):
    action_type: str = Field(..., min_length=1)
    action_class: str = Field(..., min_length=1)
    project_id: str = ""
    phase_id: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


@router.post("/check")
def check_state_authority(request: StateAuthorityCheckRequest) -> Dict[str, Any]:
    try:
        packet = build_state_authority_packet(request.model_dump())
        return {
            "status": "ok",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "state_authority": packet,
            "summary": summarize_state_authority(packet),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/summary")
def summarize_state_authority_check(request: StateAuthorityCheckRequest) -> Dict[str, Any]:
    try:
        packet = build_state_authority_packet(request.model_dump())
        return {
            "status": "ok",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "summary": summarize_state_authority(packet),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
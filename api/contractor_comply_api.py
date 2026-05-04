"""
Comply API surface for contractor_builder_v1 (governed).
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.child_cores.contractor_builder_v1.comply.comply_service import (
    run_compliance_check,
)


router = APIRouter(prefix="/comply", tags=["contractor_comply"])


class ComplyRunRequest(BaseModel):
    project_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    actor: str = "contractor_comply_api"


@router.post("/run")
def run_comply(request: ComplyRunRequest) -> Dict[str, Any]:
    try:
        return run_compliance_check(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
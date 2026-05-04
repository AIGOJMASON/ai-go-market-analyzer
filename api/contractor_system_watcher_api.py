from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.core.watcher.contractor_system_watcher import watch_contractor_system


router = APIRouter(prefix="/system-watcher", tags=["contractor_system_watcher"])


class ContractorSystemWatcherRequest(BaseModel):
    project_id: str
    phase_id: str = ""
    report: Dict[str, Any] = Field(default_factory=dict)


@router.post("/check")
def check_contractor_system(request: ContractorSystemWatcherRequest) -> Dict[str, Any]:
    try:
        return watch_contractor_system(
            project_id=request.project_id,
            phase_id=request.phase_id,
            report=request.report,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.core.state_runtime.state_reader import read_contractor_project_state


router = APIRouter(prefix="/project-record", tags=["contractor_project_record"])


class ContractorProjectRecordRequest(BaseModel):
    project_id: str


def _clean_required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


@router.get("/health")
def contractor_project_record_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "route": "contractor_project_record",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": False,
        "purpose": "Expose contractor project state as a read-only project record surface.",
    }


@router.post("/read")
def read_project_record(request: ContractorProjectRecordRequest) -> Dict[str, Any]:
    project_id = _clean_required(request.project_id, "project_id")

    try:
        state = read_contractor_project_state(project_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "project_record_read_failed",
                "message": str(exc),
            },
        ) from exc

    if state.get("project_exists") is not True:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "project_not_found",
                "project_id": project_id,
            },
        )

    return {
        "status": "ok",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": False,
        "project_id": project_id,
        "project_state": state,
    }
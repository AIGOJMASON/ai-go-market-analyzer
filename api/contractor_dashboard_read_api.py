from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.core.state_runtime.contractor_dashboard_read_context import (
    build_dashboard_read_context,
)


router = APIRouter(prefix="/dashboard-read", tags=["contractor_dashboard_read"])


class ContractorDashboardReadRequest(BaseModel):
    project_id: str
    persist_packet: bool = False  # NORTHSTAR FIX: default must be False


def _clean_required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


@router.get("/health")
def contractor_dashboard_read_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": False,
        "purpose": "Build dashboard read context without implicit persistence.",
    }


@router.post("/run")
def run_dashboard_read(request: ContractorDashboardReadRequest) -> Dict[str, Any]:
    project_id = _clean_required(request.project_id, "project_id")

    try:
        result = build_dashboard_read_context(
            project_id=project_id,
            persist_packet=bool(request.persist_packet),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "dashboard_read_failed",
                "message": str(exc),
            },
        ) from exc

    return {
        "status": "ok",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": bool(request.persist_packet),
        "project_id": project_id,
        "persist_packet": bool(request.persist_packet),
        "dashboard": result,
    }
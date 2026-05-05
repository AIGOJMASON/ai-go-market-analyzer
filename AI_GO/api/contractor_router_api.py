"""
Router API surface for contractor_builder_v1 (governed).
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.router.router_service import (
    persist_schedule_blocks_governed,
)
from AI_GO.child_cores.contractor_builder_v1.router.capacity_detector import (
    build_capacity_snapshot,
)
from AI_GO.child_cores.contractor_builder_v1.router.cascade_risk_runtime import (
    build_cascade_risk_from_conflicts,
)
from AI_GO.child_cores.contractor_builder_v1.router.conflict_detector import (
    detect_schedule_conflicts,
)

router = APIRouter(prefix="/router", tags=["contractor_router"])


class RouterBlocksRequest(BaseModel):
    project_id: str
    blocks: List[Dict[str, Any]]
    actor: str = "contractor_router_api"


class RouterAnalyzeRequest(BaseModel):
    project_id: str
    blocks: List[Dict[str, Any]]
    capacity_limits: Dict[str, int] = {}
    report_id: str = "router-report"


@router.post("/blocks")
def persist_schedule_blocks(request: RouterBlocksRequest) -> dict:
    try:
        return persist_schedule_blocks_governed(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/analyze")
def analyze_router(request: RouterAnalyzeRequest) -> dict:
    try:
        conflicts = detect_schedule_conflicts(
            project_id=request.project_id,
            blocks=request.blocks,
        )

        capacity_records = build_capacity_snapshot(
            project_id=request.project_id,
            blocks=request.blocks,
            capacity_limits=request.capacity_limits,
        )

        cascade = build_cascade_risk_from_conflicts(
            project_id=request.project_id,
            report_id=request.report_id,
            conflicts=conflicts,
            capacity_records=capacity_records,
        )

        return {
            "status": "ok",
            "conflicts": conflicts,
            "capacity_records": capacity_records,
            "cascade_risk": cascade,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
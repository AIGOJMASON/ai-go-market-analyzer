"""
Router API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.router.schedule_block_runtime import (
    upsert_schedule_blocks,
)
from AI_GO.child_cores.contractor_builder_v1.router.conflict_detector import (
    detect_schedule_conflicts,
)
from AI_GO.child_cores.contractor_builder_v1.router.capacity_detector import (
    build_capacity_snapshot,
)
from AI_GO.child_cores.contractor_builder_v1.router.cascade_risk_runtime import (
    build_cascade_risk_from_conflicts,
)
from AI_GO.child_cores.contractor_builder_v1.router.router_receipt_builder import (
    build_router_receipt,
    write_router_receipt,
)

router = APIRouter(prefix="/router", tags=["contractor_router"])


class RouterBlocksRequest(BaseModel):
    project_id: str
    blocks: List[Dict[str, Any]]


class RouterAnalyzeRequest(BaseModel):
    project_id: str
    blocks: List[Dict[str, Any]]
    capacity_limits: Dict[str, int] = {}
    report_id: str = "router-report"


@router.post("/blocks")
def persist_schedule_blocks(request: RouterBlocksRequest) -> dict:
    try:
        output_path = upsert_schedule_blocks(
            project_id=request.project_id,
            blocks=request.blocks,
        )
        receipt = build_router_receipt(
            event_type="store_schedule_blocks",
            project_id=request.project_id,
            artifact_path=str(output_path),
        )
        receipt_path = write_router_receipt(receipt)

        return {
            "status": "stored",
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
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

        receipt = build_router_receipt(
            event_type="run_conflict_scan",
            project_id=request.project_id,
            artifact_path=f"runtime://router/{request.project_id}/analysis",
            details={"conflict_count": len(conflicts)},
        )

        return {
            "status": "ok",
            "conflicts": conflicts,
            "capacity_records": capacity_records,
            "cascade_risk": cascade,
            "receipt": receipt,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
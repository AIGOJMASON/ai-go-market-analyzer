"""
Compliance API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.comply.permit_runtime import (
    generate_required_permits,
)
from AI_GO.child_cores.contractor_builder_v1.comply.inspection_runtime import (
    generate_required_inspections,
)
from AI_GO.child_cores.contractor_builder_v1.comply.snapshot_runtime import (
    build_snapshot,
)
from AI_GO.child_cores.contractor_builder_v1.comply.code_lookup_runtime import (
    lookup_code,
)
from AI_GO.child_cores.contractor_builder_v1.comply.comply_receipt_builder import (
    build_compliance_receipt,
)

router = APIRouter(prefix="/comply", tags=["contractor_comply"])


class ComplianceSnapshotRequest(BaseModel):
    project_id: str
    jurisdiction: str
    permits: List[Dict[str, Any]] = []
    inspections: List[Dict[str, Any]] = []


class ComplianceCodeLookupRequest(BaseModel):
    jurisdiction: str
    category: str


@router.post("/required")
def get_required_compliance(payload: Dict[str, str]) -> dict:
    try:
        project_id = payload["project_id"]
        jurisdiction = payload["jurisdiction"]

        permits = generate_required_permits(project_id=project_id, jurisdiction=jurisdiction)
        inspections = generate_required_inspections(project_id=project_id, jurisdiction=jurisdiction)

        return {
            "status": "ok",
            "permits": permits,
            "inspections": inspections,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/snapshot")
def build_compliance_snapshot(request: ComplianceSnapshotRequest) -> dict:
    try:
        permits = request.permits or generate_required_permits(
            project_id=request.project_id,
            jurisdiction=request.jurisdiction,
        )
        inspections = request.inspections or generate_required_inspections(
            project_id=request.project_id,
            jurisdiction=request.jurisdiction,
        )
        snapshot = build_snapshot(
            project_id=request.project_id,
            permits=permits,
            inspections=inspections,
        )
        receipt = build_compliance_receipt(
            project_id=request.project_id,
            snapshot=snapshot,
        )
        return {
            "status": "ok",
            "snapshot": snapshot,
            "receipt": receipt,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/code-lookup")
def contractor_code_lookup(request: ComplianceCodeLookupRequest) -> dict:
    try:
        result = lookup_code(
            jurisdiction=request.jurisdiction,
            category=request.category,
        )
        return {
            "status": "ok",
            "result": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
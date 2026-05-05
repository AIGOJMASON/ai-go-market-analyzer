"""
Risk API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_runtime import (
    create_risk_record,
    append_risk_record,
    transition_risk_status,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.review_runtime import (
    review_risk_entry,
    build_risk_review_record,
    risk_requires_review,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_receipt_builder import (
    build_risk_receipt,
    write_risk_receipt,
)

router = APIRouter(prefix="/risk", tags=["contractor_risk"])


class RiskCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]


class RiskTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str
    notes: str = ""


class RiskReviewRequest(BaseModel):
    entry: Dict[str, Any]
    reviewer_name: str
    reviewer_role: str
    notes: str = ""


@router.post("/create")
def create_risk_entry(request: RiskCreateRequest) -> dict:
    try:
        entry = create_risk_record(**request.entry_kwargs)
        output_path = append_risk_record(entry)
        receipt = build_risk_receipt(
            event_type="create_risk",
            project_id=entry["project_id"],
            risk_id=entry["risk_id"],
            artifact_path=str(output_path),
        )
        receipt_path = write_risk_receipt(receipt)
        return {
            "status": "created",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/review")
def review_risk(request: RiskReviewRequest) -> dict:
    try:
        reviewed = review_risk_entry(
            request.entry,
            reviewer_name=request.reviewer_name,
            reviewer_role=request.reviewer_role,
            notes=request.notes,
        )
        output_path = append_risk_record(reviewed)
        review_record = build_risk_review_record(
            project_id=reviewed["project_id"],
            risk_id=reviewed["risk_id"],
            reviewer_name=request.reviewer_name,
            reviewer_role=request.reviewer_role,
            previous_status=request.entry.get("status", ""),
            current_status=reviewed.get("status", ""),
            notes=request.notes,
        )
        receipt = build_risk_receipt(
            event_type="review_risk",
            project_id=reviewed["project_id"],
            risk_id=reviewed["risk_id"],
            artifact_path=str(output_path),
        )
        receipt_path = write_risk_receipt(receipt)
        return {
            "status": "reviewed",
            "entry": reviewed,
            "review_record": review_record,
            "requires_review_now": risk_requires_review(reviewed),
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_risk(request: RiskTransitionRequest) -> dict:
    try:
        entry = transition_risk_status(
            request.entry,
            new_status=request.new_status,
            notes=request.notes,
        )
        output_path = append_risk_record(entry)
        receipt = build_risk_receipt(
            event_type="change_risk_status",
            project_id=entry["project_id"],
            risk_id=entry["risk_id"],
            artifact_path=str(output_path),
            details={"new_status": request.new_status},
        )
        receipt_path = write_risk_receipt(receipt)
        return {
            "status": "transitioned",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
"""
Assumption API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_runtime import (
    create_assumption_record,
    append_assumption_record,
    transition_assumption_status,
)
from AI_GO.child_cores.contractor_builder_v1.assumption_log.invalidation_conversion import (
    build_invalidation_conversion_record,
)
from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_receipt_builder import (
    build_assumption_receipt,
    write_assumption_receipt,
)

router = APIRouter(prefix="/assumption", tags=["contractor_assumption"])


class AssumptionCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]


class AssumptionTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str
    notes: str = ""


class AssumptionInvalidateRequest(BaseModel):
    entry: Dict[str, Any]
    actor_name: str
    actor_role: str
    conversion_option: str
    linked_decision_id: str = ""
    linked_change_packet_id: str = ""
    linked_risk_id: str = ""
    rationale: str = ""


@router.post("/create")
def create_assumption_entry(request: AssumptionCreateRequest) -> dict:
    try:
        entry = create_assumption_record(**request.entry_kwargs)
        output_path = append_assumption_record(entry)
        receipt = build_assumption_receipt(
            event_type="create_assumption",
            project_id=entry["project_id"],
            assumption_id=entry["assumption_id"],
            artifact_path=str(output_path),
        )
        receipt_path = write_assumption_receipt(receipt)
        return {
            "status": "created",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_assumption(request: AssumptionTransitionRequest) -> dict:
    try:
        entry = transition_assumption_status(
            request.entry,
            new_status=request.new_status,
            notes=request.notes,
        )
        output_path = append_assumption_record(entry)
        receipt = build_assumption_receipt(
            event_type="change_assumption_status",
            project_id=entry["project_id"],
            assumption_id=entry["assumption_id"],
            artifact_path=str(output_path),
            details={"new_status": request.new_status},
        )
        receipt_path = write_assumption_receipt(receipt)
        return {
            "status": "transitioned",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/invalidate")
def invalidate_assumption(request: AssumptionInvalidateRequest) -> dict:
    try:
        invalidated = transition_assumption_status(
            request.entry,
            new_status="Invalidated",
            notes=request.rationale,
        )
        output_path = append_assumption_record(invalidated)

        conversion_record = build_invalidation_conversion_record(
            project_id=invalidated["project_id"],
            assumption_id=invalidated["assumption_id"],
            conversion_option=request.conversion_option,
            actor_name=request.actor_name,
            actor_role=request.actor_role,
            linked_decision_id=request.linked_decision_id,
            linked_change_packet_id=request.linked_change_packet_id,
            linked_risk_id=request.linked_risk_id,
            rationale=request.rationale,
        )

        receipt = build_assumption_receipt(
            event_type="invalidate_assumption",
            project_id=invalidated["project_id"],
            assumption_id=invalidated["assumption_id"],
            artifact_path=str(output_path),
            details={"conversion_option": request.conversion_option},
        )
        receipt_path = write_assumption_receipt(receipt)

        return {
            "status": "invalidated",
            "entry": invalidated,
            "conversion_record": conversion_record,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
"""
Decision API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_runtime import (
    create_decision_record,
    append_decision_record,
    transition_decision_status,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.dual_ack_policy import (
    apply_requester_signature,
    apply_approver_signature,
    can_submit_decision,
    can_enter_approver_review,
    can_approve_decision,
    can_reject_decision,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_receipt_builder import (
    build_decision_receipt,
    write_decision_receipt,
)

router = APIRouter(prefix="/decision", tags=["contractor_decision"])


class DecisionCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]


class DecisionSignatureRequest(BaseModel):
    entry: Dict[str, Any]
    signer_type: str
    name: str
    role: str
    org: str
    signature: str


class DecisionTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str


@router.post("/create")
def create_decision_entry(request: DecisionCreateRequest) -> dict:
    try:
        entry = create_decision_record(**request.entry_kwargs)
        output_path = append_decision_record(entry)
        receipt = build_decision_receipt(
            event_type="create_decision",
            project_id=entry["project_id"],
            decision_id=entry["decision_id"],
            artifact_path=str(output_path),
        )
        receipt_path = write_decision_receipt(receipt)
        return {
            "status": "created",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sign")
def sign_decision_entry(request: DecisionSignatureRequest) -> dict:
    try:
        entry = dict(request.entry)

        if request.signer_type == "requester":
            entry = apply_requester_signature(
                entry,
                name=request.name,
                role=request.role,
                org=request.org,
                signature=request.signature,
            )
        elif request.signer_type == "approver":
            entry = apply_approver_signature(
                entry,
                name=request.name,
                role=request.role,
                org=request.org,
                signature=request.signature,
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid signer_type")

        return {
            "status": "signed",
            "entry": entry,
            "readiness": {
                "can_submit": can_submit_decision(entry),
                "can_enter_approver_review": can_enter_approver_review(entry),
                "can_approve": can_approve_decision(entry),
                "can_reject": can_reject_decision(entry),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_decision_entry(request: DecisionTransitionRequest) -> dict:
    try:
        entry = transition_decision_status(request.entry, new_status=request.new_status)
        output_path = append_decision_record(entry)

        event_type_map = {
            "requester_submitted": "submit_decision",
            "approver_review": "review_decision",
            "approved": "approve_decision",
            "rejected": "reject_decision",
        }

        receipt_path = None
        if request.new_status in event_type_map:
            receipt = build_decision_receipt(
                event_type=event_type_map[request.new_status],
                project_id=entry["project_id"],
                decision_id=entry["decision_id"],
                artifact_path=str(output_path),
            )
            receipt_path = str(write_decision_receipt(receipt))

        return {
            "status": "transitioned",
            "entry": entry,
            "artifact_path": str(output_path),
            "receipt_path": receipt_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
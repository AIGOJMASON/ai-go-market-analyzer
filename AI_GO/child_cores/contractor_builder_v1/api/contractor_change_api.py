"""
Change API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from AI_GO.child_cores.contractor_builder_v1.change.change_runtime import (
    create_change_packet_record,
    append_change_packet_record,
    append_change_approval_event,
    transition_change_packet_status,
)
from AI_GO.child_cores.contractor_builder_v1.change.approval_runtime import (
    can_submit_change_packet,
    can_move_to_pending_approvals,
    can_approve_change_packet,
    apply_requester_signature,
    apply_approver_signature,
    apply_pm_signature,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_receipt_builder import (
    build_change_receipt,
    write_change_receipt,
)

router = APIRouter(prefix="/change", tags=["contractor_change"])


class ChangeCreateRequest(BaseModel):
    packet_kwargs: Dict[str, Any]


class ChangeStatusRequest(BaseModel):
    packet: Dict[str, Any]
    new_status: str


class ChangeSignatureRequest(BaseModel):
    packet: Dict[str, Any]
    signer_type: str
    name: str
    signature: str


@router.post("/create")
def create_change_packet(request: ChangeCreateRequest) -> dict:
    try:
        packet = create_change_packet_record(**request.packet_kwargs)
        output_path = append_change_packet_record(packet)
        receipt = build_change_receipt(
            event_type="create_change_packet",
            project_id=packet["project_id"],
            change_packet_id=packet["change_packet_id"],
            artifact_path=str(output_path),
        )
        receipt_path = write_change_receipt(receipt)
        return {
            "status": "created",
            "packet": packet,
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sign")
def sign_change_packet(request: ChangeSignatureRequest) -> dict:
    try:
        packet = dict(request.packet)

        if request.signer_type == "requester":
            packet = apply_requester_signature(packet, name=request.name, signature=request.signature)
        elif request.signer_type == "approver":
            packet = apply_approver_signature(packet, name=request.name, signature=request.signature)
        elif request.signer_type == "pm":
            packet = apply_pm_signature(packet, name=request.name, signature=request.signature)
        else:
            raise HTTPException(status_code=400, detail="Invalid signer_type")

        return {
            "status": "signed",
            "packet": packet,
            "readiness": {
                "can_submit": can_submit_change_packet(packet),
                "can_move_to_pending_approvals": can_move_to_pending_approvals(packet),
                "can_approve": can_approve_change_packet(packet),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_change_packet(request: ChangeStatusRequest) -> dict:
    try:
        packet = transition_change_packet_status(
            request.packet,
            new_status=request.new_status,
        )
        output_path = append_change_packet_record(packet)

        event_type_map = {
            "requester_submitted": "submit_change_packet",
            "priced": "price_change_packet",
            "approved": "approve_change_packet",
            "rejected": "reject_change_packet",
            "archived": "archive_change_packet",
        }

        receipt_path = None
        if request.new_status in event_type_map:
            receipt = build_change_receipt(
                event_type=event_type_map[request.new_status],
                project_id=packet["project_id"],
                change_packet_id=packet["change_packet_id"],
                artifact_path=str(output_path),
            )
            receipt_path = str(write_change_receipt(receipt))

        append_change_approval_event(
            project_id=packet["project_id"],
            change_packet_id=packet["change_packet_id"],
            event_type=request.new_status,
            actor_name="api",
            actor_role="system_surface",
        )

        return {
            "status": "transitioned",
            "packet": packet,
            "artifact_path": str(output_path),
            "receipt_path": receipt_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
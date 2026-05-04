from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.change.approval_runtime import (
    apply_approver_signature,
    apply_pm_signature,
    apply_requester_signature,
    can_approve_change_packet,
    can_move_to_pending_approvals,
    can_submit_change_packet,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_receipt_builder import (
    build_change_receipt,
    write_change_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_runtime import (
    append_change_approval_event,
    append_change_packet_record,
    create_change_packet_record,
    get_latest_change_packet,
    transition_change_packet_status,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_policy import (
    build_change_signoff_policy_summary,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_status_runtime import (
    get_latest_change_signoff_status,
)


def execute_change_create(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet_kwargs = dict(request.get("packet_kwargs", {}))

    packet = create_change_packet_record(**packet_kwargs)
    output_path = append_change_packet_record(packet)

    receipt = build_change_receipt(
        event_type="create_change_packet",
        project_id=packet["project_id"],
        change_packet_id=packet["change_packet_id"],
        artifact_path=str(output_path),
        actor=str(request.get("actor", "change_executor")),
    )
    receipt_path = write_change_receipt(receipt)

    policy_summary = build_change_signoff_policy_summary(packet)

    return {
        "status": "created",
        "packet": packet,
        "policy_summary": policy_summary,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }


def execute_change_sign(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet = dict(context["packet"])

    signer_type = str(request.get("signer_type", "")).strip().lower()
    name = str(request.get("name", "")).strip()
    signature = str(request.get("signature", "")).strip()

    if signer_type == "requester":
        packet = apply_requester_signature(
            packet,
            name=name,
            signature=signature,
        )
    elif signer_type == "approver":
        packet = apply_approver_signature(
            packet,
            name=name,
            signature=signature,
        )
    elif signer_type == "pm":
        packet = apply_pm_signature(
            packet,
            name=name,
            signature=signature,
        )
    else:
        raise ValueError("Invalid signer_type")

    policy_summary = build_change_signoff_policy_summary(packet)

    return {
        "status": "signed",
        "packet": packet,
        "policy_summary": policy_summary,
        "readiness": {
            "can_submit": can_submit_change_packet(packet),
            "can_move_to_pending_approvals": can_move_to_pending_approvals(packet),
            "can_approve": can_approve_change_packet(packet),
        },
    }


def execute_change_transition(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    packet = dict(context["packet"])
    new_status = str(request.get("new_status", "")).strip()
    actor = str(request.get("actor", "change_executor")).strip() or "change_executor"

    packet = transition_change_packet_status(
        packet,
        new_status=new_status,
    )
    output_path = append_change_packet_record(packet)

    event_type_map = {
        "requester_submitted": "submit_change_packet",
        "approved": "approve_change_packet",
        "rejected": "reject_change_packet",
        "archived": "archive_change_packet",
    }

    receipt_path = None
    if new_status in event_type_map:
        receipt = build_change_receipt(
            event_type=event_type_map[new_status],
            project_id=packet["project_id"],
            change_packet_id=packet["change_packet_id"],
            artifact_path=str(output_path),
            actor=actor,
        )
        receipt_path = str(write_change_receipt(receipt))

    latest_signoff_status = get_latest_change_signoff_status(
        project_id=str(packet.get("project_id", "")).strip(),
        change_packet_id=str(packet.get("change_packet_id", "")).strip(),
    )

    policy_summary = build_change_signoff_policy_summary(
        packet,
        latest_signoff_status=latest_signoff_status,
    )

    return {
        "status": "transitioned",
        "packet": packet,
        "policy_summary": policy_summary,
        "artifact_path": str(output_path),
        "receipt_path": receipt_path,
    }


def execute_change_approval_event(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])

    output_path = append_change_approval_event(
        project_id=str(request.get("project_id", "")).strip(),
        change_packet_id=str(request.get("change_packet_id", "")).strip(),
        event_type=str(request.get("event_type", "")).strip(),
        actor_name=str(request.get("actor_name", "")).strip(),
        actor_role=str(request.get("actor_role", "")).strip(),
        notes=str(request.get("notes", "")),
    )

    return {
        "status": "recorded",
        "artifact_path": str(output_path),
    }


def read_latest_change_packet_view(
    *,
    project_id: str,
    change_packet_id: str,
) -> Dict[str, Any]:
    packet = get_latest_change_packet(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    if not packet:
        return {
            "status": "not_found",
            "packet": {},
            "latest_signoff_status": {},
            "policy_summary": {},
        }

    latest_signoff_status = get_latest_change_signoff_status(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    policy_summary = build_change_signoff_policy_summary(
        packet,
        latest_signoff_status=latest_signoff_status,
    )

    return {
        "status": "ok",
        "packet": packet,
        "latest_signoff_status": latest_signoff_status or {},
        "policy_summary": policy_summary,
    }
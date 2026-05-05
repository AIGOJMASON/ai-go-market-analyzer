from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_receipt_builder import (
    build_decision_receipt,
    write_decision_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_runtime import (
    append_decision_record,
    create_decision_record,
    transition_decision_status,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.dual_ack_policy import (
    apply_approver_signature,
    apply_requester_signature,
    can_approve_decision,
    can_enter_approver_review,
    can_reject_decision,
    can_submit_decision,
)


def _gate_allowed(execution_gate: Dict[str, Any]) -> bool:
    return bool((execution_gate or {}).get("allowed") is True)


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not _gate_allowed(execution_gate):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Decision executor refused to write because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )


def execute_create_decision(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    entry_kwargs = dict(payload.get("entry_kwargs", {}))
    actor = str(payload.get("actor", "decision_executor")).strip() or "decision_executor"

    entry = create_decision_record(**entry_kwargs)
    output_path = append_decision_record(entry)

    receipt = build_decision_receipt(
        event_type="create_decision",
        project_id=entry["project_id"],
        decision_id=entry["decision_id"],
        artifact_path=str(output_path),
        actor=actor,
    )
    receipt_path = write_decision_receipt(receipt)

    return {
        "status": "created",
        "entry": entry,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }


def execute_sign_decision(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    entry = dict(payload.get("entry", {}))
    signer_type = str(payload.get("signer_type", "")).strip()

    if signer_type == "requester":
        entry = apply_requester_signature(
            entry,
            name=str(payload.get("name", "")),
            role=str(payload.get("role", "")),
            org=str(payload.get("org", "")),
            signature=str(payload.get("signature", "")),
        )
    elif signer_type == "approver":
        entry = apply_approver_signature(
            entry,
            name=str(payload.get("name", "")),
            role=str(payload.get("role", "")),
            org=str(payload.get("org", "")),
            signature=str(payload.get("signature", "")),
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


def execute_transition_decision(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    actor = str(payload.get("actor", "decision_executor")).strip() or "decision_executor"
    new_status = str(payload.get("new_status", "")).strip()

    entry = transition_decision_status(
        dict(payload.get("entry", {})),
        new_status=new_status,
    )
    output_path = append_decision_record(entry)

    event_type_map = {
        "requester_submitted": "submit_decision",
        "approver_review": "review_decision",
        "approved": "approve_decision",
        "rejected": "reject_decision",
    }

    receipt_path: Optional[str] = None
    if new_status in event_type_map:
        receipt = build_decision_receipt(
            event_type=event_type_map[new_status],
            project_id=entry["project_id"],
            decision_id=entry["decision_id"],
            artifact_path=str(output_path),
            actor=actor,
        )
        receipt_path = str(write_decision_receipt(receipt))

    return {
        "status": "transitioned",
        "entry": entry,
        "artifact_path": str(output_path),
        "receipt_path": receipt_path,
    }
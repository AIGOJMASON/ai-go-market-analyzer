from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.risk_register.review_runtime import (
    build_risk_review_record,
    review_risk_entry,
    risk_requires_review,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_receipt_builder import (
    build_risk_receipt,
    write_risk_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_runtime import (
    append_risk_record,
    create_risk_record,
    transition_risk_status,
)


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not bool((execution_gate or {}).get("allowed") is True):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Risk executor refused to write because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )


def execute_create_risk(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    actor = str(payload.get("actor", "risk_executor")).strip() or "risk_executor"
    entry_kwargs = dict(payload.get("entry_kwargs", {}))

    entry = create_risk_record(**entry_kwargs)
    output_path = append_risk_record(entry)

    receipt = build_risk_receipt(
        event_type="create_risk",
        project_id=entry["project_id"],
        risk_id=entry["risk_id"],
        artifact_path=str(output_path),
        actor=actor,
    )
    receipt_path = write_risk_receipt(receipt)

    return {
        "status": "created",
        "entry": entry,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }


def execute_review_risk(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    actor = str(payload.get("actor", "risk_executor")).strip() or "risk_executor"
    entry = dict(payload.get("entry", {}))
    reviewer_name = str(payload.get("reviewer_name", "")).strip()
    reviewer_role = str(payload.get("reviewer_role", "")).strip()
    notes = str(payload.get("notes", "")).strip()

    reviewed = review_risk_entry(
        entry,
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role,
        notes=notes,
    )

    output_path = append_risk_record(reviewed)

    review_record = build_risk_review_record(
        project_id=reviewed["project_id"],
        risk_id=reviewed["risk_id"],
        reviewer_name=reviewer_name,
        reviewer_role=reviewer_role,
        previous_status=entry.get("status", ""),
        current_status=reviewed.get("status", ""),
        notes=notes,
    )

    receipt = build_risk_receipt(
        event_type="review_risk",
        project_id=reviewed["project_id"],
        risk_id=reviewed["risk_id"],
        artifact_path=str(output_path),
        actor=actor,
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


def execute_transition_risk(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    actor = str(payload.get("actor", "risk_executor")).strip() or "risk_executor"
    entry = dict(payload.get("entry", {}))
    new_status = str(payload.get("new_status", "")).strip()
    notes = str(payload.get("notes", "")).strip()

    updated = transition_risk_status(
        entry,
        new_status=new_status,
        notes=notes,
    )

    output_path = append_risk_record(updated)

    receipt = build_risk_receipt(
        event_type="change_risk_status",
        project_id=updated["project_id"],
        risk_id=updated["risk_id"],
        artifact_path=str(output_path),
        actor=actor,
        details={"new_status": new_status},
    )
    receipt_path = write_risk_receipt(receipt)

    return {
        "status": "transitioned",
        "entry": updated,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }
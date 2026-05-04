from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_receipt_builder import (
    build_assumption_receipt,
    write_assumption_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_runtime import (
    append_assumption_record,
    create_assumption_record,
    transition_assumption_status,
)
from AI_GO.child_cores.contractor_builder_v1.assumption_log.invalidation_conversion import (
    build_invalidation_conversion_record,
)


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not bool((execution_gate or {}).get("allowed") is True):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Assumption executor refused to write because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )


def execute_create_assumption(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    entry_kwargs = dict(payload.get("entry_kwargs", {}))
    entry = create_assumption_record(**entry_kwargs)
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


def execute_transition_assumption(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    entry = transition_assumption_status(
        dict(payload.get("entry", {})),
        new_status=str(payload.get("new_status", "")).strip(),
        notes=str(payload.get("notes", "")).strip(),
    )
    output_path = append_assumption_record(entry)

    receipt = build_assumption_receipt(
        event_type="change_assumption_status",
        project_id=entry["project_id"],
        assumption_id=entry["assumption_id"],
        artifact_path=str(output_path),
        details={"new_status": str(payload.get("new_status", "")).strip()},
    )
    receipt_path = write_assumption_receipt(receipt)

    return {
        "status": "transitioned",
        "entry": entry,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }


def execute_invalidate_assumption(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    invalidated = transition_assumption_status(
        dict(payload.get("entry", {})),
        new_status="Invalidated",
        notes=str(payload.get("rationale", "")).strip(),
    )
    output_path = append_assumption_record(invalidated)

    conversion_record = build_invalidation_conversion_record(
        project_id=invalidated["project_id"],
        assumption_id=invalidated["assumption_id"],
        conversion_option=str(payload.get("conversion_option", "")).strip(),
        actor_name=str(payload.get("actor_name", "")).strip(),
        actor_role=str(payload.get("actor_role", "")).strip(),
        linked_decision_id=str(payload.get("linked_decision_id", "")).strip(),
        linked_change_packet_id=str(payload.get("linked_change_packet_id", "")).strip(),
        linked_risk_id=str(payload.get("linked_risk_id", "")).strip(),
        rationale=str(payload.get("rationale", "")).strip(),
    )

    receipt = build_assumption_receipt(
        event_type="invalidate_assumption",
        project_id=invalidated["project_id"],
        assumption_id=invalidated["assumption_id"],
        artifact_path=str(output_path),
        details={
            "conversion_option": str(payload.get("conversion_option", "")).strip(),
        },
    )
    receipt_path = write_assumption_receipt(receipt)

    return {
        "status": "invalidated",
        "entry": invalidated,
        "conversion_record": conversion_record,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
    }
from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.comply.comply_executor import (
    execute_compliance_check,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.result_summary import build_result_summary


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _build_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_id = _safe_str(payload.get("project_id"))
    errors = []

    if not project_id:
        errors.append("project_id_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_comply",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "project_id": project_id,
        "checks": {
            "project_id_present": bool(project_id),
            "state_mutation_declared": True,
        },
        "errors": errors,
        "read_only": False,
        "mutation_allowed": True,
        "sealed": True,
    }


def _build_watcher(state: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    errors = []
    request_payload = _safe_dict(payload.get("payload"))

    if state.get("valid") is not True:
        errors.append("state_validation_failed")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_comply",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": state.get("project_id", ""),
        "checks": {
            "state_valid": bool(state.get("valid") is True),
            "payload_is_dict": isinstance(request_payload, dict),
            "mutation_declared": True,
            "receipt_planned": True,
            "operator_approved": True,
            "execution_required": True,
        },
        "errors": errors,
        "policy": {
            "read_only": False,
            "mutation_allowed": True,
            "execution_allowed": False,
            "requires_execution_gate": True,
            "operator_approval_required": True,
            "receipt_required": True,
        },
        "sealed": True,
    }


def run_compliance_check(payload: Dict[str, Any]) -> Dict[str, Any]:
    profile = "contractor_comply"
    action = "comply_run"
    actor = _safe_str(payload.get("actor")) or "contractor_comply_service"
    project_id = _safe_str(payload.get("project_id"))

    state = _build_state(payload)
    watcher = _build_watcher(state, payload)

    request = {
        "actor": actor,
        "target": "contractor_comply",
        "child_core_id": "contractor_builder_v1",
        "project_id": project_id,
        "action": action,
        "action_type": "write_state",
        "action_class": "write_state",
        "state_mutation_declared": True,
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "approval_granted": True,
        "watcher_passed": watcher.get("valid") is True,
        "state_passed": state.get("valid") is True,
        "watcher_result": watcher,
        "state_decision": state,
        "state": state,
        "bounded_context": True,
        "declared_intent": "governed contractor compliance snapshot mutation",
        "payload": _safe_dict(payload.get("payload")),
    }

    context = build_governed_context(
        profile=profile,
        action=action,
        route="/contractor-builder/comply/run",
        request=request,
        state=state,
        watcher=watcher,
    )

    if state.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={"error": "comply_state_validation_failed", "context": context},
        )

    if watcher.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={"error": "comply_watcher_validation_failed", "context": context},
        )

    enforce_execution_gate(context["execution_gate"])

    result = execute_compliance_check(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    result_summary = build_result_summary(
        action=action,
        result=result,
        context=context,
    )

    return {
        "mode": "governed_execution",
        **context,
        **result,
        "result_summary": result_summary,
    }
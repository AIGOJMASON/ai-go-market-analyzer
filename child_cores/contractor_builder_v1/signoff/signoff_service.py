from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.signoff.signoff_executor import (
    execute_signoff_complete,
    execute_signoff_decline,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.client_signoff_status_runtime import (
    get_latest_client_signoff_status,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    reconcile_workflow_state,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_contractor_signoff_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import watch_contractor_signoff


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def _empty_state(
    *,
    project_id: str,
    phase_id: str,
    action: str,
    error: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "state_validation",
        "profile": "contractor_signoff",
        "status": "failed",
        "valid": False,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": {"action": action},
        "errors": [error],
        "matched_phase": {},
        "latest_signoff_status": {},
        "sealed": True,
    }


def _empty_watcher(
    *,
    project_id: str,
    phase_id: str,
    action: str,
    error: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_signoff",
        "status": "failed",
        "valid": False,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": {"action": action},
        "errors": [error],
        "sealed": True,
    }


def _build_context(
    *,
    payload: Dict[str, Any],
    action: str,
) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    phase_id = _required(payload.get("phase_id"), "phase_id")
    actor = _required(payload.get("actor", "signoff_service"), "actor")

    route_suffix = "complete" if action == "signoff_complete" else "decline"

    try:
        reconciliation = reconcile_workflow_state(
            project_id=project_id,
            actor=actor,
        )
    except Exception as exc:
        state = _empty_state(
            project_id=project_id,
            phase_id=phase_id,
            action=action,
            error=f"workflow_reconciliation_failed:{type(exc).__name__}",
        )
        watcher = _empty_watcher(
            project_id=project_id,
            phase_id=phase_id,
            action=action,
            error="watcher_not_run_state_failed",
        )

        context = build_governed_context(
            profile="contractor_signoff",
            action=action,
            route=f"/contractor-builder/signoff/{route_suffix}",
            request={
                "project_id": project_id,
                "phase_id": phase_id,
                "actor": actor,
            },
            state=state,
            watcher=watcher,
        )

        raise HTTPException(
            status_code=409,
            detail={
                "error": "workflow_reconciliation_failed",
                "message": str(exc),
                "state": state,
                "watcher": watcher,
                "governance_decision": context.get("governance_decision", {}),
            },
        )

    workflow_state = dict(reconciliation.get("workflow_state", {}))
    phase_instances = list(reconciliation.get("phase_instances", []))

    latest_signoff_status = reconciliation.get("latest_signoff_status")
    if latest_signoff_status is None:
        latest_signoff_status = get_latest_client_signoff_status(
            project_id=project_id,
            phase_id=phase_id,
        )

    state = validate_contractor_signoff_state(
        project_id=project_id,
        phase_id=phase_id,
        workflow_state=workflow_state,
        phase_instances=phase_instances,
        latest_signoff_status=latest_signoff_status
        if isinstance(latest_signoff_status, dict)
        else None,
        action=action,
    )

    watcher = watch_contractor_signoff(
        project_id=project_id,
        phase_id=phase_id,
        action=action,
        latest_signoff_status=latest_signoff_status
        if isinstance(latest_signoff_status, dict)
        else None,
        workflow_state=workflow_state,
    )

    context = build_governed_context(
        profile="contractor_signoff",
        action=action,
        route=f"/contractor-builder/signoff/{route_suffix}",
        request={
            "project_id": project_id,
            "phase_id": phase_id,
            "actor": actor,
        },
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            status_code=409,
            error="signoff_state_validation_failed",
            message="Signoff state validation failed before execution.",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            status_code=409,
            error="signoff_watcher_validation_failed",
            message="Signoff watcher validation failed before execution.",
            context=context,
        )

    return {
        **context,
        "project_id": project_id,
        "phase_id": phase_id,
        "actor": actor,
        "workflow_state": workflow_state,
        "phase_instances": phase_instances,
        "latest_signoff_status": latest_signoff_status or {},
        "reconciliation": reconciliation,
    }


def check_signoff_complete(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(
        payload=payload,
        action="signoff_complete",
    )

    return {
        "status": "ok",
        "mode": "check_only",
        **context,
    }


def complete_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(
        payload=payload,
        action="signoff_complete",
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_signoff_complete(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def check_signoff_decline(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(
        payload=payload,
        action="signoff_decline",
    )

    return {
        "status": "ok",
        "mode": "check_only",
        **context,
    }


def decline_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(
        payload=payload,
        action="signoff_decline",
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_signoff_decline(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }
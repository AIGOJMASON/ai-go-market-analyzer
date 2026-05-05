from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.change.change_closeout_guard import (
    build_change_closeout_guard_summary,
)
from AI_GO.child_cores.contractor_builder_v1.phase_closeout.phase_closeout_executor import (
    execute_phase_closeout,
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
from AI_GO.core.governance.governance_packet_store import (
    attach_result_summary_to_governance_packet,
)
from AI_GO.core.governance.result_summary import build_result_summary
from AI_GO.core.paths.path_resolver import get_contractor_project_root
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_contractor_phase_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import (
    watch_contractor_phase_closeout,
)


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def _optional(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _project_name(project_id: str, request_project_name: str) -> str:
    request_clean = str(request_project_name or "").strip()
    if request_clean:
        return request_clean

    project_profile_path = get_contractor_project_root(project_id) / "project_profile.json"

    if project_profile_path.exists():
        try:
            payload = json.loads(project_profile_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                name = str(payload.get("project_name", "")).strip()
                if name:
                    return name
        except Exception:
            pass

    return project_id


def _phase_name(instance: Dict[str, Any], fallback_phase_id: str) -> str:
    return str(instance.get("phase_name", "")).strip() or fallback_phase_id


def _empty_state(
    *,
    project_id: str,
    phase_id: str,
    error: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "state_validation",
        "profile": "contractor_phase_closeout",
        "status": "failed",
        "valid": False,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": {},
        "errors": [error],
        "matched_phase": {},
        "sealed": True,
    }


def _empty_watcher(
    *,
    project_id: str,
    phase_id: str,
    error: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_phase_closeout",
        "status": "failed",
        "valid": False,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": {},
        "errors": [error],
        "sealed": True,
    }


def _apply_execution_override_if_allowed(
    *,
    context: Dict[str, Any],
    state: Dict[str, Any],
    watcher: Dict[str, Any],
    execution_override: bool,
    operator_approved: bool,
) -> Dict[str, Any]:
    """
    Controlled execution override.

    This does not bypass state or watcher. It only converts the governance and
    execution gate decision to allowed after state and watcher have already
    passed. This is used by the explicit execution certification probe.
    """
    if not execution_override:
        return context

    if state.get("valid") is not True:
        return context

    if watcher.get("valid") is not True:
        return context

    updated = dict(context)

    governance_decision = dict(updated.get("governance_decision", {}))
    governance_decision["allowed"] = True
    governance_decision["status"] = "allowed"
    governance_decision["blocked"] = False
    governance_decision["reason"] = "execution_override_after_state_and_watcher_pass"
    governance_decision["execution_override"] = True
    governance_decision["operator_approved"] = bool(operator_approved)
    governance_decision["approval_required"] = False
    updated["governance_decision"] = governance_decision

    execution_gate = dict(updated.get("execution_gate", {}))
    execution_gate["allowed"] = True
    execution_gate["status"] = "allowed"
    execution_gate["blocked"] = False
    execution_gate["reason"] = "execution_override_after_state_and_watcher_pass"
    execution_gate["execution_override"] = True
    execution_gate["operator_approved"] = bool(operator_approved)
    execution_gate["approval_required"] = False
    updated["execution_gate"] = execution_gate

    return updated


def _build_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    phase_id = _required(payload.get("phase_id"), "phase_id")
    client_email = _required(payload.get("client_email"), "client_email")
    client_name = _required(payload.get("client_name", "Customer"), "client_name")
    actor = _optional(payload.get("actor"), "phase_closeout_service")
    allow_resend = bool(payload.get("allow_resend_if_sent", True))
    project_name = _project_name(project_id, str(payload.get("project_name", "")))

    operator_approved = bool(payload.get("operator_approved", False))
    execution_override = bool(payload.get("execution_override", False))

    request_payload = {
        "project_id": project_id,
        "phase_id": phase_id,
        "actor": actor,
        "client_email": client_email,
        "client_name": client_name,
        "project_name": project_name,
        "allow_resend_if_sent": allow_resend,
        "operator_approved": operator_approved,
        "execution_override": execution_override,
    }

    try:
        reconciliation = reconcile_workflow_state(
            project_id=project_id,
            actor=actor,
        )
    except Exception as exc:
        state = _empty_state(
            project_id=project_id,
            phase_id=phase_id,
            error=f"workflow_reconciliation_failed:{type(exc).__name__}",
        )
        watcher = _empty_watcher(
            project_id=project_id,
            phase_id=phase_id,
            error="watcher_not_run_state_failed",
        )

        context = build_governed_context(
            profile="contractor_phase_closeout",
            action="phase_closeout",
            route="/contractor-builder/phase-closeout/run",
            request=request_payload,
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
    checklist_summary = dict(reconciliation.get("checklist_summary", {}))

    state = validate_contractor_phase_state(
        project_id=project_id,
        phase_id=phase_id,
        workflow_state=workflow_state,
        phase_instances=phase_instances,
    )

    if not state.get("valid"):
        watcher = _empty_watcher(
            project_id=project_id,
            phase_id=phase_id,
            error="watcher_not_run_state_failed",
        )

        context = build_governed_context(
            profile="contractor_phase_closeout",
            action="phase_closeout",
            route="/contractor-builder/phase-closeout/run",
            request=request_payload,
            state=state,
            watcher=watcher,
        )

        raise_governance_failure(
            status_code=409,
            error="phase_closeout_state_validation_failed",
            message="Phase closeout state validation failed before execution.",
            context=context,
        )

    phase_instance = dict(state.get("matched_phase", {}))
    phase_name = _phase_name(phase_instance, phase_id)

    latest_signoff_status = reconciliation.get("latest_signoff_status")
    if latest_signoff_status is None:
        latest_signoff_status = get_latest_client_signoff_status(
            project_id=project_id,
            phase_id=phase_id,
        )

    change_closeout_guard = build_change_closeout_guard_summary(
        project_id=project_id,
        phase_id=phase_id,
    )

    watcher = watch_contractor_phase_closeout(
        project_id=project_id,
        phase_id=phase_id,
        checklist_summary=checklist_summary,
        change_closeout_guard=change_closeout_guard,
        latest_signoff_status=latest_signoff_status
        if isinstance(latest_signoff_status, dict)
        else None,
        workflow_state=workflow_state,
        allow_resend_if_sent=allow_resend,
    )

    context = build_governed_context(
        profile="contractor_phase_closeout",
        action="phase_closeout",
        route="/contractor-builder/phase-closeout/run",
        request=request_payload,
        state=state,
        watcher=watcher,
    )

    context = _apply_execution_override_if_allowed(
        context=context,
        state=state,
        watcher=watcher,
        execution_override=execution_override,
        operator_approved=operator_approved,
    )

    if not watcher.get("valid"):
        raise_governance_failure(
            status_code=409,
            error="phase_closeout_watcher_validation_failed",
            message="Phase closeout watcher validation failed before execution.",
            context=context,
        )

    return {
        **context,
        "project_id": project_id,
        "phase_id": phase_id,
        "client_email": client_email,
        "client_name": client_name,
        "actor": actor,
        "project_name": project_name,
        "phase_name": phase_name,
        "workflow_state": workflow_state,
        "phase_instance": phase_instance,
        "checklist_summary": checklist_summary,
        "latest_signoff_status": latest_signoff_status or {},
        "change_closeout_guard": change_closeout_guard,
        "email_subject": str(payload.get("email_subject", "") or "").strip(),
        "email_body": str(payload.get("email_body", "") or "").strip(),
        "operator_approved": operator_approved,
        "execution_override": execution_override,
        "reconciliation": reconciliation,
    }


def _attach_result_summary(context: Dict[str, Any], result_summary: Dict[str, Any]) -> Dict[str, Any]:
    governance_decision = _safe_dict(context.get("governance_decision"))
    governance_packet_id = str(governance_decision.get("governance_packet_id", "")).strip()
    profile = str(governance_decision.get("profile", "contractor_phase_closeout")).strip()

    if not governance_packet_id:
        return {
            "status": "not_attached",
            "reason": "missing_governance_packet_id",
        }

    try:
        return attach_result_summary_to_governance_packet(
            profile=profile,
            governance_packet_id=governance_packet_id,
            result_summary=result_summary,
        )
    except Exception as exc:
        return {
            "status": "not_attached",
            "reason": f"{type(exc).__name__}:{exc}",
            "governance_packet_id": governance_packet_id,
        }


def check_phase_closeout(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(payload)

    return {
        "status": "ok",
        "mode": "check_only",
        **context,
    }


def run_phase_closeout(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _build_context(payload)

    enforce_execution_gate(context["execution_gate"])

    result = execute_phase_closeout(
        context=context,
        execution_gate=context["execution_gate"],
    )

    result_summary = build_result_summary(
        action="phase_closeout",
        result=result,
        context=context,
    )

    result_summary_persistence = _attach_result_summary(context, result_summary)

    return {
        "mode": "governed_execution",
        **context,
        **result,
        "result_summary": result_summary,
        "result_summary_persistence": result_summary_persistence,
    }
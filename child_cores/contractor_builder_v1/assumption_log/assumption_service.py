from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_executor import (
    execute_create_assumption,
    execute_invalidate_assumption,
    execute_transition_assumption,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.result_summary import build_result_summary


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _project_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))

    return (
        str(payload.get("project_id", "")).strip()
        or str(entry_kwargs.get("project_id", "")).strip()
        or str(entry.get("project_id", "")).strip()
    )


def _assumption_id_from_payload(payload: Dict[str, Any]) -> str:
    entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
    entry = _safe_dict(payload.get("entry"))

    return (
        str(payload.get("assumption_id", "")).strip()
        or str(entry_kwargs.get("assumption_id", "")).strip()
        or str(entry.get("assumption_id", "")).strip()
    )


def _route_for_action(action: str) -> str:
    if action == "assumption_create":
        return "/contractor-builder/assumption/create"
    if action == "assumption_transition":
        return "/contractor-builder/assumption/transition"
    if action == "assumption_invalidate":
        return "/contractor-builder/assumption/invalidate"
    return "/contractor-builder/assumption"


def _build_state(
    *,
    profile: str,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _project_id_from_payload(payload)
    assumption_id = _assumption_id_from_payload(payload)

    errors = []
    checks = {
        "project_id_present": bool(project_id),
        "action_present": bool(action),
        "profile_present": bool(profile),
        "state_mutation_declared": True,
    }

    if not project_id:
        errors.append("project_id_missing")

    if action in {"assumption_transition", "assumption_invalidate"}:
        checks["assumption_id_present"] = bool(assumption_id)
        if not assumption_id:
            errors.append("assumption_id_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "project_id": project_id,
        "assumption_id": assumption_id,
        "checks": checks,
        "errors": errors,
        "read_only": False,
        "mutation_allowed": True,
        "sealed": True,
    }


def _build_watcher(
    *,
    profile: str,
    action: str,
    state: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    errors = []
    checks = {
        "state_valid": bool(state.get("valid") is True),
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "execution_required": True,
    }

    if state.get("valid") is not True:
        errors.append("state_validation_failed")

    if action == "assumption_create":
        entry_kwargs = _safe_dict(payload.get("entry_kwargs"))
        checks["entry_kwargs_present"] = bool(entry_kwargs)
        if not entry_kwargs:
            errors.append("entry_kwargs_missing")

    if action == "assumption_transition":
        new_status = str(payload.get("new_status", "")).strip()
        checks["new_status_present"] = bool(new_status)
        if not new_status:
            errors.append("new_status_missing")

    if action == "assumption_invalidate":
        conversion_option = str(payload.get("conversion_option", "")).strip()
        actor_name = str(payload.get("actor_name", "")).strip()
        actor_role = str(payload.get("actor_role", "")).strip()

        checks["conversion_option_present"] = bool(conversion_option)
        checks["actor_name_present"] = bool(actor_name)
        checks["actor_role_present"] = bool(actor_role)

        if not conversion_option:
            errors.append("conversion_option_missing")
        if not actor_name:
            errors.append("actor_name_missing")
        if not actor_role:
            errors.append("actor_role_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": state.get("project_id", ""),
        "assumption_id": state.get("assumption_id", ""),
        "checks": checks,
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


def _govern(
    *,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    profile = "contractor_assumption"
    actor = str(payload.get("actor", "contractor_assumption_service")).strip()
    project_id = _project_id_from_payload(payload)
    assumption_id = _assumption_id_from_payload(payload)

    state = _build_state(profile=profile, action=action, payload=payload)
    watcher = _build_watcher(
        profile=profile,
        action=action,
        state=state,
        payload=payload,
    )

    request = {
        "actor": actor,
        "target": "contractor_assumption",
        "child_core_id": "contractor_builder_v1",
        "project_id": project_id,
        "assumption_id": assumption_id,
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
        "declared_intent": "governed contractor assumption state mutation",
    }

    context = build_governed_context(
        profile=profile,
        action=action,
        route=_route_for_action(action),
        request=request,
        state=state,
        watcher=watcher,
    )

    if state.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "assumption_state_validation_failed",
                "context": context,
            },
        )

    if watcher.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "assumption_watcher_validation_failed",
                "context": context,
            },
        )

    return context


def _finish(
    *,
    action: str,
    context: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
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


def create_assumption(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="assumption_create", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_create_assumption(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="assumption_create", context=context, result=result)


def transition_assumption(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="assumption_transition", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_transition_assumption(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="assumption_transition", context=context, result=result)


def invalidate_assumption(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _govern(action="assumption_invalidate", payload=payload)
    enforce_execution_gate(context["execution_gate"])

    result = execute_invalidate_assumption(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    return _finish(action="assumption_invalidate", context=context, result=result)
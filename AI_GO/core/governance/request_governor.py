from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from AI_GO.core.canon_runtime.canon_enforcer import enforce_canon_action_from_dict
from AI_GO.core.execution_gate.execution_gate_policy import evaluate_execution_gate
from AI_GO.core.state_runtime.state_authority import build_state_authority_packet
from AI_GO.core.watcher.root_watcher import evaluate_root_watcher


REQUEST_GOVERNOR_VERSION = "v1.6"


MUTATION_OR_EXECUTION_CLASSES = {
    "write_state",
    "workflow_transition",
    "send_delivery",
    "execute",
}


MUTATION_OR_EXECUTION_TYPES = {
    "execute",
    "dispatch",
    "send_email",
    "send_delivery",
    "write_state",
    "mutate_state",
    "phase_closeout",
    "send_phase_closeout",
    "close_phase",
    "record_signoff",
    "complete_signoff",
    "decline_signoff",
    "workflow_initialize",
    "workflow_checklist_upsert",
    "workflow_reconcile",
    "workflow_repair_upsert",
    "workflow_signoff_status_update",
}


@dataclass(frozen=True)
class GovernedRequest:
    request_id: str = ""
    route: str = ""
    method: str = ""
    actor: str = "unknown"
    target: str = ""
    child_core_id: str = ""

    action_type: str = ""
    action_class: str = ""

    project_id: str = ""
    phase_id: str = ""

    payload: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _base_decision(request: GovernedRequest) -> Dict[str, Any]:
    return {
        "status": "pending",
        "allowed": False,
        "valid": False,
        "decision": "pending",
        "governor_version": REQUEST_GOVERNOR_VERSION,
        "checked_at": _utc_now_iso(),
        "request": {
            "request_id": request.request_id,
            "route": request.route,
            "method": request.method,
            "actor": request.actor,
            "target": request.target,
            "child_core_id": request.child_core_id,
            "action_type": request.action_type,
            "action_class": request.action_class,
            "project_id": request.project_id,
            "phase_id": request.phase_id,
        },
        "stages": {
            "state": {
                "status": "not_run",
                "allowed": False,
                "decision": {},
            },
            "watcher": {
                "status": "not_run",
                "allowed": False,
                "decision": {},
            },
            "canon": {
                "status": "not_run",
                "allowed": False,
                "decision": {},
            },
            "execution_gate": {
                "status": "not_required",
                "allowed": None,
                "decision": {},
            },
        },
        "rejection_reasons": [],
        "warnings": [],
        "message": "",
    }


def _reject(
    result: Dict[str, Any],
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    result["rejection_reasons"].append(
        {
            "code": code,
            "message": message,
            "details": details or {},
        }
    )


def _warn(result: Dict[str, Any], code: str, message: str) -> None:
    result["warnings"].append(
        {
            "code": code,
            "message": message,
        }
    )


def build_governed_request(
    *,
    request_id: str = "",
    route: str = "",
    method: str = "",
    actor: str = "unknown",
    target: str = "",
    child_core_id: str = "",
    action_type: str = "",
    action_class: str = "",
    project_id: str = "",
    phase_id: str = "",
    payload: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> GovernedRequest:
    return GovernedRequest(
        request_id=_clean(request_id),
        route=_clean(route),
        method=_clean(method).upper(),
        actor=_clean(actor) or "unknown",
        target=_clean(target),
        child_core_id=_clean(child_core_id),
        action_type=_clean(action_type),
        action_class=_clean(action_class),
        project_id=_clean(project_id),
        phase_id=_clean(phase_id),
        payload=dict(payload or {}),
        context=dict(context or {}),
    )


def build_governed_request_from_dict(payload: Dict[str, Any]) -> GovernedRequest:
    source = _dict(payload)

    return build_governed_request(
        request_id=source.get("request_id", ""),
        route=source.get("route", ""),
        method=source.get("method", ""),
        actor=source.get("actor", "unknown"),
        target=source.get("target", ""),
        child_core_id=source.get("child_core_id", ""),
        action_type=source.get("action_type", ""),
        action_class=source.get("action_class", ""),
        project_id=source.get("project_id", ""),
        phase_id=source.get("phase_id", ""),
        payload=_dict(source.get("payload")),
        context=_dict(source.get("context")),
    )


def _validate_request_shape(request: GovernedRequest, result: Dict[str, Any]) -> None:
    if not request.action_type:
        _reject(
            result,
            "missing_action_type",
            "Request Governor requires action_type before enforcement.",
        )

    if not request.action_class:
        _reject(
            result,
            "missing_action_class",
            "Request Governor requires action_class before enforcement.",
        )

    if not request.actor or request.actor == "unknown":
        _reject(
            result,
            "missing_actor",
            "Request Governor requires actor for authority and audit.",
        )

    if not request.route:
        _warn(
            result,
            "missing_route",
            "Route is missing. Enforcement can continue, but route lineage is weaker.",
        )


def _build_state_authority_payload(request: GovernedRequest) -> Dict[str, Any]:
    return {
        "request_id": request.request_id,
        "route": request.route,
        "method": request.method,
        "actor": request.actor,
        "target": request.target,
        "child_core_id": request.child_core_id,
        "action_type": request.action_type,
        "action_class": request.action_class,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "payload": dict(request.payload),
        "context": dict(request.context),
    }


def _phase_instance_from_state_decision(
    *,
    state_decision: Dict[str, Any],
    phase_id: str,
) -> Dict[str, Any]:
    state_validation = _dict(state_decision.get("state_validation"))
    matched_phase = _dict(state_validation.get("matched_phase"))
    if matched_phase:
        return matched_phase

    state_context = _dict(state_validation.get("state_context"))
    phase_instances = _list(state_context.get("phase_instances"))

    for phase in phase_instances:
        if isinstance(phase, dict) and _clean(phase.get("phase_id")) == phase_id:
            return dict(phase)

    return {}


def _workflow_state_from_state_decision(state_decision: Dict[str, Any]) -> Dict[str, Any]:
    state_validation = _dict(state_decision.get("state_validation"))
    state_context = _dict(state_validation.get("state_context"))

    workflow_state = _dict(state_context.get("workflow_state"))
    if workflow_state:
        return workflow_state

    checks = _dict(state_validation.get("checks"))
    current_phase_id = _clean(checks.get("current_phase_id"))
    project_id = _clean(state_validation.get("project_id"))

    if current_phase_id or project_id:
        return {
            "project_id": project_id,
            "current_phase_id": current_phase_id,
        }

    return {}


def _checklist_summary_from_context_or_payload(request: GovernedRequest) -> Dict[str, Any]:
    for candidate in (
        request.context.get("checklist_summary"),
        request.payload.get("checklist_summary"),
        request.context.get("checklist"),
        request.payload.get("checklist"),
    ):
        as_dict = _dict(candidate)
        if as_dict:
            return as_dict

    return {}


def _change_closeout_guard_from_context_or_payload(request: GovernedRequest) -> Dict[str, Any]:
    for candidate in (
        request.context.get("change_closeout_guard"),
        request.payload.get("change_closeout_guard"),
    ):
        as_dict = _dict(candidate)
        if as_dict:
            return as_dict

    return {}


def _receipt_planned(request: GovernedRequest) -> bool:
    return (
        request.context.get("receipt_planned") is True
        or request.payload.get("receipt_planned") is True
        or bool(_clean(request.context.get("receipt_id")))
        or bool(_clean(request.payload.get("receipt_id")))
        or bool(_clean(request.context.get("receipt_path")))
        or bool(_clean(request.payload.get("receipt_path")))
        or bool(_list(request.context.get("receipt_paths")))
        or bool(_list(request.payload.get("receipt_paths")))
    )


def _operator_approved(request: GovernedRequest) -> bool:
    return (
        request.context.get("operator_approved") is True
        or request.payload.get("operator_approved") is True
        or request.context.get("approval_granted") is True
        or request.payload.get("approval_granted") is True
    )


def _state_mutation_declared(request: GovernedRequest) -> bool:
    return (
        request.context.get("state_mutation_declared") is True
        or request.payload.get("state_mutation_declared") is True
        or request.context.get("mutation_declared") is True
        or request.payload.get("mutation_declared") is True
    )


def _cross_core_integrity_passed(request: GovernedRequest) -> bool:
    if (
        request.context.get("cross_core_integrity_passed") is True
        or request.context.get("cross_core_passed") is True
        or request.payload.get("cross_core_integrity_passed") is True
        or request.payload.get("cross_core_passed") is True
    ):
        return True

    if request.context.get("external_source") is True or request.payload.get("external_source") is True:
        return False

    if request.context.get("raw_input") is True or request.payload.get("raw_input") is True:
        return False

    return bool(request.route and request.target)


def _requires_execution_gate(request: GovernedRequest) -> bool:
    if request.context.get("execution_intent") is True:
        return True

    if request.payload.get("execution_intent") is True:
        return True

    if request.action_class in MUTATION_OR_EXECUTION_CLASSES:
        return True

    if request.action_type in MUTATION_OR_EXECUTION_TYPES:
        return True

    return False


def _build_watcher_payload(
    *,
    request: GovernedRequest,
    state_decision: Dict[str, Any],
) -> Dict[str, Any]:
    workflow_state = _workflow_state_from_state_decision(state_decision)
    phase_instance = _phase_instance_from_state_decision(
        state_decision=state_decision,
        phase_id=request.phase_id,
    )

    checklist_summary = _checklist_summary_from_context_or_payload(request)
    change_closeout_guard = _change_closeout_guard_from_context_or_payload(request)

    return {
        "request_id": request.request_id,
        "route": request.route,
        "method": request.method,
        "actor": request.actor,
        "target": request.target,
        "child_core_id": request.child_core_id,
        "action_type": request.action_type,
        "action_class": request.action_class,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "watcher_profile": request.context.get("watcher_profile") or request.payload.get("watcher_profile") or "",
        "watcher_required": _requires_execution_gate(request),
        "execution_intent": _requires_execution_gate(request),
        "state_authority_passed": state_decision.get("allowed") is True,
        "state_passed": state_decision.get("allowed") is True,
        "state_mutation_declared": _state_mutation_declared(request),
        "receipt_planned": _receipt_planned(request),
        "operator_approved": _operator_approved(request),
        "workflow_state": workflow_state,
        "phase_instance": phase_instance,
        "checklist_summary": checklist_summary,
        "change_closeout_guard": change_closeout_guard,
        "supplied_watcher_result": _dict(request.context.get("watcher_result")),
        "bypass_watcher": request.context.get("bypass_watcher") is True or request.payload.get("bypass_watcher") is True,
        "bypass_execution_gate": request.context.get("bypass_execution_gate") is True or request.payload.get("bypass_execution_gate") is True,
        "hidden_state_mutation": request.context.get("hidden_state_mutation") is True or request.payload.get("hidden_state_mutation") is True,
        "watcher_override": request.context.get("watcher_override") is True or request.payload.get("watcher_override") is True,
        "governance_override": request.context.get("governance_override") is True or request.payload.get("governance_override") is True,
        "payload": dict(request.payload),
        "context": dict(request.context),
    }


def _build_canon_action(
    request: GovernedRequest,
    *,
    state_decision: Dict[str, Any],
    watcher_decision: Dict[str, Any],
) -> Dict[str, Any]:
    context = dict(request.context)
    payload = dict(request.payload)

    if request.request_id:
        context.setdefault("request_id", request.request_id)

    if request.child_core_id:
        context.setdefault("child_core_id", request.child_core_id)

    workflow_state = _workflow_state_from_state_decision(state_decision)
    if workflow_state:
        context["workflow_state"] = workflow_state

    phase_instance = _phase_instance_from_state_decision(
        state_decision=state_decision,
        phase_id=request.phase_id,
    )
    if phase_instance:
        context["phase_instance"] = phase_instance

    checklist_summary = _checklist_summary_from_context_or_payload(request)
    if checklist_summary:
        context["checklist_summary"] = checklist_summary

    context["state_authority"] = state_decision
    context["state_passed"] = state_decision.get("allowed") is True
    context["watcher_result"] = watcher_decision
    context["watcher_passed"] = watcher_decision.get("allowed") is True

    payload.setdefault("state_passed", state_decision.get("allowed") is True)
    payload.setdefault("watcher_passed", watcher_decision.get("allowed") is True)

    return {
        "action_type": request.action_type,
        "action_class": request.action_class,
        "actor": request.actor,
        "target": request.target,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "route": request.route,
        "payload": payload,
        "context": context,
    }


def _build_execution_gate_context(
    *,
    request: GovernedRequest,
    state_decision: Dict[str, Any],
    watcher_decision: Dict[str, Any],
    canon_decision: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "request_id": request.request_id,
        "route": request.route,
        "method": request.method,
        "actor": request.actor,
        "target": request.target,
        "child_core_id": request.child_core_id,
        "action_type": request.action_type,
        "action_class": request.action_class,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "state_authority_passed": state_decision.get("allowed") is True,
        "state_passed": state_decision.get("allowed") is True,
        "watcher_passed": watcher_decision.get("allowed") is True,
        "canon_passed": canon_decision.get("allowed") is True,
        "governor_passed": True,
        "operator_approved": _operator_approved(request),
        "receipt_planned": _receipt_planned(request),
        "cross_core_integrity_passed": _cross_core_integrity_passed(request),
        "cross_core_passed": _cross_core_integrity_passed(request),
        "raw_input": (
            request.context.get("raw_input") is True
            or request.payload.get("raw_input") is True
        ),
        "external_source": (
            request.context.get("external_source") is True
            or request.payload.get("external_source") is True
        ),
        "requires_research_lineage": (
            request.context.get("requires_research_lineage") is True
            or request.payload.get("requires_research_lineage") is True
        ),
        "research_lineage": (
            request.context.get("research_lineage") is True
            or request.payload.get("research_lineage") is True
        ),
        "engine_processed": (
            request.context.get("engine_processed") is True
            or request.payload.get("engine_processed") is True
        ),
        "adapter_applied": (
            request.context.get("adapter_applied") is True
            or request.payload.get("adapter_applied") is True
        ),
        "payload": dict(request.payload),
        "context": dict(request.context),
    }


def govern_request(request: GovernedRequest) -> Dict[str, Any]:
    result = _base_decision(request)

    _validate_request_shape(request, result)

    if result["rejection_reasons"]:
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        result["message"] = "Request blocked before state, watcher, canon, or execution enforcement."
        return result

    state_decision = build_state_authority_packet(_build_state_authority_payload(request))
    result["stages"]["state"] = {
        "status": state_decision.get("status", "unknown"),
        "allowed": state_decision.get("allowed") is True,
        "decision": state_decision,
    }

    if state_decision.get("allowed") is not True:
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        _reject(
            result,
            "state_authority_blocked",
            "State Authority blocked this request before Watcher, Canon, or Execution Gate.",
            {
                "state_errors": state_decision.get("errors", []),
                "state_warnings": state_decision.get("warnings", []),
                "state_required": state_decision.get("state_required"),
                "state_passed": state_decision.get("state_passed"),
            },
        )
        result["message"] = "Request blocked by State Authority."
        return result

    watcher_decision = evaluate_root_watcher(
        _build_watcher_payload(
            request=request,
            state_decision=state_decision,
        )
    )

    result["stages"]["watcher"] = {
        "status": watcher_decision.get("status", "unknown"),
        "allowed": watcher_decision.get("allowed") is True,
        "decision": watcher_decision,
    }

    if watcher_decision.get("allowed") is not True:
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        _reject(
            result,
            "watcher_blocked",
            "Root Watcher blocked this request before Canon or Execution Gate.",
            {
                "watcher_errors": watcher_decision.get("errors", []),
                "watcher_warnings": watcher_decision.get("warnings", []),
            },
        )
        result["message"] = "Request blocked by Root Watcher."
        return result

    canon_action = _build_canon_action(
        request,
        state_decision=state_decision,
        watcher_decision=watcher_decision,
    )
    canon_decision = enforce_canon_action_from_dict(canon_action)

    result["stages"]["canon"] = {
        "status": canon_decision.get("status", "unknown"),
        "allowed": canon_decision.get("allowed") is True,
        "decision": canon_decision,
    }

    if canon_decision.get("allowed") is not True:
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        _reject(
            result,
            "canon_enforcement_blocked",
            "Canon Enforcer blocked this request.",
            {
                "canon_rejection_reasons": canon_decision.get("rejection_reasons", []),
            },
        )
        result["message"] = "Request blocked by Canon Enforcer."
        return result

    if _requires_execution_gate(request):
        execution_gate_decision = evaluate_execution_gate(
            _build_execution_gate_context(
                request=request,
                state_decision=state_decision,
                watcher_decision=watcher_decision,
                canon_decision=canon_decision,
            )
        )

        result["stages"]["execution_gate"] = {
            "status": execution_gate_decision.get("status", "unknown"),
            "allowed": execution_gate_decision.get("allowed") is True,
            "decision": execution_gate_decision,
        }

        if execution_gate_decision.get("allowed") is not True:
            result["status"] = "blocked"
            result["decision"] = "block"
            result["allowed"] = False
            result["valid"] = False
            _reject(
                result,
                "execution_gate_blocked",
                "Execution Gate blocked this request.",
                {
                    "execution_gate_reasons": execution_gate_decision.get("reasons", []),
                },
            )
            result["message"] = "Request blocked by Execution Gate."
            return result

    result["status"] = "passed"
    result["decision"] = "allow"
    result["allowed"] = True
    result["valid"] = True
    result["message"] = (
        "Request passed State Authority, Root Watcher, Canon Enforcer, and Execution Gate."
        if _requires_execution_gate(request)
        else "Request passed State Authority, Root Watcher, and Canon Enforcer."
    )

    return result


def govern_request_from_dict(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = build_governed_request_from_dict(payload)
    return govern_request(request)


def assert_request_allowed(payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = govern_request_from_dict(payload)

    if decision.get("allowed") is not True:
        raise PermissionError(decision)

    return decision
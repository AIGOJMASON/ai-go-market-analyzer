from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from AI_GO.core.governance.request_governor import govern_request_from_dict


MUTATION_GUARD_VERSION = "mutation_guard_v1.1"
MUTATION_GUARD_6B_LAYER_VERSION = "northstar_6b_mutation_guard_v1"

REQUIRED_MUTATION_STANDARD_FIELDS = {
    "execution_intent": True,
    "state_mutation_declared": True,
    "receipt_planned": True,
    "operator_approved": True,
}

MUTATING_ACTION_CLASSES = {
    "write_state",
    "workflow_transition",
    "send_delivery",
    "execute",
}

MUTATING_ACTION_TYPES = {
    "phase_closeout",
    "send_phase_closeout",
    "close_phase",
    "record_signoff",
    "complete_signoff",
    "decline_signoff",
    "write_state",
    "mutate_state",
    "write_receipt",
    "generate_artifact",
    "send_email",
    "send_external",
    "call_external_service",
    "create_decision",
    "transition_decision",
    "create_change",
    "transition_change",
    "create_assumption",
    "invalidate_assumption",
    "workflow_transition",
    "project_create",
}

ALLOWED_MUTATION_CLASSES = {
    "workflow_state_transition",
    "phase_closeout_execution",
    "phase_closeout_persistence",
    "delivery_execution",
    "receipt_write",
    "artifact_generation",
    "state_write",
    "governed_service_execution",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _dict(value: Any) -> Dict[str, Any]:
    return _as_dict(value)


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _bool(value: Any) -> bool:
    return value is True


def _dedupe(values: List[str]) -> List[str]:
    return sorted({_clean(value) for value in values if _clean(value)})


def _standard_error(
    *,
    code: str,
    message: str,
    request_payload: Dict[str, Any],
) -> PermissionError:
    return PermissionError(
        {
            "error": code,
            "message": message,
            "mutation_guard_version": MUTATION_GUARD_VERSION,
            "request_payload": request_payload,
        }
    )


def _normalize_mutation_payload(
    *,
    request_id: str,
    route: str,
    method: str,
    actor: str,
    target: str,
    child_core_id: str,
    action_type: str,
    action_class: str,
    project_id: str = "",
    phase_id: str = "",
    payload: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized_payload = dict(payload or {})
    normalized_context = dict(context or {})

    normalized_payload["execution_intent"] = True
    normalized_context["execution_intent"] = True

    normalized_payload["state_mutation_declared"] = True
    normalized_context["state_mutation_declared"] = True

    return {
        "request_id": _clean(request_id),
        "route": _clean(route),
        "method": _clean(method).upper(),
        "actor": _clean(actor),
        "target": _clean(target),
        "child_core_id": _clean(child_core_id),
        "action_type": _clean(action_type),
        "action_class": _clean(action_class),
        "project_id": _clean(project_id),
        "phase_id": _clean(phase_id),
        "payload": normalized_payload,
        "context": normalized_context,
    }


def _validate_mutation_standard(request_payload: Dict[str, Any]) -> None:
    payload = _dict(request_payload.get("payload"))
    context = _dict(request_payload.get("context"))

    if not _bool(payload.get("execution_intent")) or not _bool(context.get("execution_intent")):
        raise _standard_error(
            code="mutation_standard_missing_execution_intent",
            message="Mutation requires execution_intent=true in payload and context.",
            request_payload=request_payload,
        )

    if not (
        _bool(payload.get("state_mutation_declared"))
        and _bool(context.get("state_mutation_declared"))
    ):
        raise _standard_error(
            code="mutation_standard_missing_state_mutation_declared",
            message="Mutation requires state_mutation_declared=true in payload and context.",
            request_payload=request_payload,
        )

    if not (_bool(payload.get("receipt_planned")) and _bool(context.get("receipt_planned"))):
        raise _standard_error(
            code="mutation_standard_missing_receipt_planned",
            message="Mutation requires receipt_planned=true before governance.",
            request_payload=request_payload,
        )

    if not (_bool(payload.get("operator_approved")) and _bool(context.get("operator_approved"))):
        raise _standard_error(
            code="mutation_standard_missing_operator_approved",
            message="Mutation requires operator_approved=true before governance.",
            request_payload=request_payload,
        )

    if payload.get("bypass_execution_gate") is True or context.get("bypass_execution_gate") is True:
        raise _standard_error(
            code="mutation_standard_bypass_execution_gate",
            message="Mutation may not request bypass_execution_gate.",
            request_payload=request_payload,
        )

    if payload.get("hidden_state_mutation") is True or context.get("hidden_state_mutation") is True:
        raise _standard_error(
            code="mutation_standard_hidden_state_mutation",
            message="Mutation may not hide state mutation.",
            request_payload=request_payload,
        )


def require_governed_mutation(
    *,
    request_id: str,
    route: str,
    method: str,
    actor: str,
    target: str,
    child_core_id: str,
    action_type: str,
    action_class: str,
    project_id: str = "",
    phase_id: str = "",
    payload: Dict[str, Any] | None = None,
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request_payload = _normalize_mutation_payload(
        request_id=request_id,
        route=route,
        method=method,
        actor=actor,
        target=target,
        child_core_id=child_core_id,
        action_type=action_type,
        action_class=action_class,
        project_id=project_id,
        phase_id=phase_id,
        payload=payload,
        context=context,
    )

    _validate_mutation_standard(request_payload)

    decision = govern_request_from_dict(request_payload)

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "mutation_guard_blocked",
                "mutation_guard_version": MUTATION_GUARD_VERSION,
                "governance_decision": decision,
            }
        )

    execution_stage = _dict(_dict(decision.get("stages")).get("execution_gate"))

    if execution_stage and execution_stage.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "mutation_guard_execution_gate_not_passed",
                "mutation_guard_version": MUTATION_GUARD_VERSION,
                "governance_decision": decision,
            }
        )

    return {
        "status": "passed",
        "allowed": True,
        "valid": True,
        "mutation_guard_version": MUTATION_GUARD_VERSION,
        "mutation_standard": dict(REQUIRED_MUTATION_STANDARD_FIELDS),
        "governance_decision": decision,
    }


def _base_result(
    *,
    action_type: str,
    action_class: str,
    mutation_class: str,
    persistence_type: str,
) -> Dict[str, Any]:
    return {
        "status": "pending",
        "valid": False,
        "allowed": False,
        "decision": "pending",
        "artifact_type": "northstar_mutation_guard_decision",
        "mutation_guard_version": MUTATION_GUARD_6B_LAYER_VERSION,
        "checked_at": _utc_now_iso(),
        "action": {
            "action_type": action_type,
            "action_class": action_class,
            "mutation_class": mutation_class,
            "persistence_type": persistence_type,
        },
        "required_conditions": [],
        "passed_conditions": [],
        "failed_conditions": [],
        "warnings": [],
        "errors": [],
        "message": "",
    }


def _require(result: Dict[str, Any], code: str) -> None:
    result["required_conditions"].append(code)


def _pass(result: Dict[str, Any], code: str) -> None:
    result["passed_conditions"].append(code)


def _fail(result: Dict[str, Any], code: str) -> None:
    result["failed_conditions"].append(code)
    result["errors"].append(code)


def _warn(result: Dict[str, Any], code: str) -> None:
    result["warnings"].append(code)


def _finalize(result: Dict[str, Any]) -> Dict[str, Any]:
    result["required_conditions"] = _dedupe(result["required_conditions"])
    result["passed_conditions"] = _dedupe(result["passed_conditions"])
    result["failed_conditions"] = _dedupe(result["failed_conditions"])
    result["warnings"] = _dedupe(result["warnings"])
    result["errors"] = _dedupe(result["errors"])

    allowed = not result["errors"]
    result["valid"] = allowed
    result["allowed"] = allowed
    result["decision"] = "allow" if allowed else "block"
    result["status"] = "passed" if allowed else "blocked"
    result["message"] = (
        "Mutation guard passed."
        if allowed
        else "Mutation guard blocked this action."
    )
    return result


def evaluate_mutation_guard(execution_request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(execution_request, dict):
        result = _base_result(
            action_type="",
            action_class="",
            mutation_class="",
            persistence_type="",
        )
        _fail(result, "execution_request_must_be_dict")
        return _finalize(result)

    payload = _as_dict(execution_request.get("payload"))
    context = _as_dict(execution_request.get("context"))
    trace = _as_dict(execution_request.get("trace"))
    authority = _as_dict(execution_request.get("authority"))
    mutation = _as_dict(execution_request.get("mutation"))

    action_type = _clean(execution_request.get("action_type"))
    action_class = _clean(execution_request.get("action_class"))

    mutation_class = _clean(
        execution_request.get("mutation_class")
        or mutation.get("mutation_class")
        or payload.get("mutation_class")
        or context.get("mutation_class")
    )
    persistence_type = _clean(
        execution_request.get("persistence_type")
        or mutation.get("persistence_type")
        or payload.get("persistence_type")
        or context.get("persistence_type")
    )

    result = _base_result(
        action_type=action_type,
        action_class=action_class,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
    )

    is_mutating = action_class in MUTATING_ACTION_CLASSES or action_type in MUTATING_ACTION_TYPES
    _require(result, "mutating_action_detected")
    if is_mutating:
        _pass(result, "mutating_action_detected")
    else:
        _warn(result, "non_mutating_action")
        return _finalize(result)

    _require(result, "state_mutation_declared")
    if _bool(
        execution_request.get("state_mutation_declared")
        or payload.get("state_mutation_declared")
        or context.get("state_mutation_declared")
        or mutation.get("state_mutation_declared")
    ):
        _pass(result, "state_mutation_declared")
    else:
        _fail(result, "state_mutation_not_declared")

    _require(result, "mutation_class_present")
    if mutation_class:
        _pass(result, "mutation_class_present")
    else:
        _fail(result, "mutation_class_missing")

    if mutation_class:
        _require(result, "mutation_class_known_or_explicit")
        if mutation_class in ALLOWED_MUTATION_CLASSES or mutation_class.startswith("root_"):
            _pass(result, "mutation_class_known_or_explicit")
        else:
            _warn(result, "mutation_class_not_pre_registered")

    _require(result, "persistence_type_present")
    if persistence_type:
        _pass(result, "persistence_type_present")
    else:
        _fail(result, "persistence_type_missing")

    _require(result, "receipt_planned_or_present")
    receipt_planned = _bool(
        execution_request.get("receipt_planned")
        or payload.get("receipt_planned")
        or context.get("receipt_planned")
        or mutation.get("receipt_planned")
    )
    receipt_present = bool(
        _clean(payload.get("receipt_id"))
        or _clean(context.get("receipt_id"))
        or _clean(payload.get("receipt_path"))
        or _clean(context.get("receipt_path"))
        or _as_list(payload.get("receipt_paths"))
        or _as_list(context.get("receipt_paths"))
    )
    if receipt_planned or receipt_present:
        _pass(result, "receipt_planned_or_present")
    else:
        _fail(result, "receipt_not_planned")

    _require(result, "operator_approved")
    operator_approved = _bool(
        execution_request.get("operator_approved")
        or payload.get("operator_approved")
        or context.get("operator_approved")
        or mutation.get("operator_approved")
    )
    if operator_approved:
        _pass(result, "operator_approved")
    else:
        _fail(result, "operator_approval_missing")

    _require(result, "actor_intent_authority_present")
    actor = _clean(execution_request.get("actor"))
    intent = _clean(
        execution_request.get("intent")
        or payload.get("intent")
        or context.get("intent")
        or execution_request.get("declared_intent")
        or payload.get("declared_intent")
        or context.get("declared_intent")
    )
    authority_id = _clean(
        authority.get("authority_id")
        or execution_request.get("authority_id")
        or payload.get("authority_id")
        or context.get("authority_id")
    )

    if actor and intent and authority_id:
        _pass(result, "actor_intent_authority_present")
    else:
        if not actor:
            _fail(result, "actor_missing")
        if not intent:
            _fail(result, "intent_missing")
        if not authority_id:
            _fail(result, "authority_id_missing")

    _require(result, "trace_metadata_present")
    trace_id = _clean(
        trace.get("trace_id")
        or execution_request.get("trace_id")
        or payload.get("trace_id")
        or context.get("trace_id")
        or execution_request.get("request_id")
        or context.get("request_id")
    )
    if trace_id:
        _pass(result, "trace_metadata_present")
    else:
        _fail(result, "trace_metadata_missing")

    _require(result, "execution_gate_passed")
    execution_gate = _as_dict(
        execution_request.get("execution_gate")
        or context.get("execution_gate")
    )
    if execution_gate.get("allowed") is True or execution_gate.get("valid") is True:
        _pass(result, "execution_gate_passed")
    else:
        _fail(result, "execution_gate_not_passed")

    _require(result, "governed_persistence_expected")
    if (
        _bool(mutation.get("governed_persistence"))
        or _bool(payload.get("governed_persistence"))
        or _bool(context.get("governed_persistence"))
        or bool(persistence_type)
    ):
        _pass(result, "governed_persistence_expected")
    else:
        _fail(result, "governed_persistence_not_declared")

    _require(result, "no_hidden_mutation_authority")
    hidden_flags = [
        key for key in (
            "hidden_state_mutation",
            "bypass_governed_persistence",
            "bypass_mutation_guard",
            "mutation_override",
            "bypass_execution_gate",
        )
        if authority.get(key) is True or payload.get(key) is True or context.get(key) is True
    ]
    if hidden_flags:
        for flag in hidden_flags:
            _fail(result, f"forbidden_mutation_flag_{flag}")
    else:
        _pass(result, "no_hidden_mutation_authority")

    return _finalize(result)
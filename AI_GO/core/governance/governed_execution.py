from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional

from AI_GO.core.governance.execution_gate import evaluate_execution_gate
from AI_GO.core.governance.mutation_guard import evaluate_mutation_guard
from AI_GO.core.governance.request_governor import govern_request_from_dict


GOVERNED_EXECUTION_VERSION = "northstar_6b_governed_execution_v1"


GovernedService = Callable[[Dict[str, Any]], Dict[str, Any]]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _blocked_result(
    *,
    code: str,
    message: str,
    execution_request: Dict[str, Any],
    governance_decision: Optional[Dict[str, Any]] = None,
    execution_gate: Optional[Dict[str, Any]] = None,
    mutation_guard: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "status": "blocked",
        "allowed": False,
        "valid": False,
        "executed": False,
        "artifact_type": "northstar_governed_execution_result",
        "governed_execution_version": GOVERNED_EXECUTION_VERSION,
        "checked_at": _utc_now_iso(),
        "error": {
            "code": code,
            "message": message,
        },
        "request": _safe_request_projection(execution_request),
        "stages": {
            "request_governor": governance_decision or {},
            "execution_gate": execution_gate or {},
            "mutation_guard": mutation_guard or {},
            "service": {
                "status": "not_run",
                "allowed": False,
                "result": {},
            },
        },
    }


def _safe_request_projection(execution_request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "request_id": _clean(execution_request.get("request_id")),
        "route": _clean(execution_request.get("route")),
        "method": _clean(execution_request.get("method")),
        "actor": _clean(execution_request.get("actor")),
        "target": _clean(execution_request.get("target")),
        "child_core_id": _clean(execution_request.get("child_core_id")),
        "action_type": _clean(execution_request.get("action_type")),
        "action_class": _clean(execution_request.get("action_class")),
        "project_id": _clean(execution_request.get("project_id")),
        "phase_id": _clean(execution_request.get("phase_id")),
        "mutation_class": _clean(execution_request.get("mutation_class")),
        "persistence_type": _clean(execution_request.get("persistence_type")),
    }


def normalize_execution_request(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {}

    payload = _as_dict(request.get("payload"))
    context = _as_dict(request.get("context"))
    authority = _as_dict(request.get("authority"))
    trace = _as_dict(request.get("trace"))
    mutation = _as_dict(request.get("mutation"))

    request_id = _clean(request.get("request_id") or context.get("request_id"))
    actor = _clean(request.get("actor")) or "unknown"
    action_type = _clean(request.get("action_type"))
    action_class = _clean(request.get("action_class"))

    mutation_class = _clean(
        request.get("mutation_class")
        or mutation.get("mutation_class")
        or payload.get("mutation_class")
        or context.get("mutation_class")
    )
    persistence_type = _clean(
        request.get("persistence_type")
        or mutation.get("persistence_type")
        or payload.get("persistence_type")
        or context.get("persistence_type")
    )

    normalized = dict(request)
    normalized["request_id"] = request_id
    normalized["actor"] = actor
    normalized["action_type"] = action_type
    normalized["action_class"] = action_class
    normalized["route"] = _clean(request.get("route"))
    normalized["method"] = _clean(request.get("method")).upper()
    normalized["target"] = _clean(request.get("target"))
    normalized["child_core_id"] = _clean(request.get("child_core_id"))
    normalized["project_id"] = _clean(request.get("project_id"))
    normalized["phase_id"] = _clean(request.get("phase_id"))
    normalized["mutation_class"] = mutation_class
    normalized["persistence_type"] = persistence_type

    normalized["payload"] = payload
    normalized["context"] = context
    normalized["authority"] = {
        "authority_id": _clean(authority.get("authority_id")) or "northstar_6b_governed_execution",
        "ai_execution_authority": False,
        "memory_execution_authority": False,
        "system_brain_execution_authority": False,
        "watcher_override": False,
        "state_authority_override": False,
        "canon_override": False,
        "execution_gate_override": False,
        "governance_override": False,
        "bypass_execution_gate": False,
        "hidden_state_mutation": False,
        **authority,
    }
    normalized["trace"] = {
        "trace_id": _clean(trace.get("trace_id") or request_id),
        "request_id": request_id,
        "actor": actor,
        "action_type": action_type,
        "action_class": action_class,
        "created_at": _utc_now_iso(),
        **trace,
    }
    normalized["mutation"] = {
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "receipt_planned": _bool(
            request.get("receipt_planned")
            or payload.get("receipt_planned")
            or context.get("receipt_planned")
            or mutation.get("receipt_planned")
        ),
        "state_mutation_declared": _bool(
            request.get("state_mutation_declared")
            or payload.get("state_mutation_declared")
            or context.get("state_mutation_declared")
            or mutation.get("state_mutation_declared")
        ),
        "governed_persistence": True,
        **mutation,
    }

    normalized["intent"] = _clean(
        request.get("intent")
        or request.get("declared_intent")
        or payload.get("intent")
        or payload.get("declared_intent")
        or context.get("intent")
        or context.get("declared_intent")
    )

    return normalized


def build_service_context(
    *,
    execution_request: Dict[str, Any],
    governance_decision: Dict[str, Any],
    execution_gate: Dict[str, Any],
    mutation_guard: Dict[str, Any],
) -> Dict[str, Any]:
    context = _as_dict(execution_request.get("context"))

    return {
        "request": _safe_request_projection(execution_request),
        "payload": _as_dict(execution_request.get("payload")),
        "context": context,
        "authority": _as_dict(execution_request.get("authority")),
        "trace": _as_dict(execution_request.get("trace")),
        "mutation": _as_dict(execution_request.get("mutation")),
        "governance_decision": governance_decision,
        "execution_gate": execution_gate,
        "mutation_guard": mutation_guard,
        "governed_execution": {
            "version": GOVERNED_EXECUTION_VERSION,
            "started_at": _utc_now_iso(),
            "service_receives_normalized_context": True,
            "direct_route_execution_allowed": False,
        },
    }


def execute_governed_action(
    *,
    request: Dict[str, Any],
    service: GovernedService,
) -> Dict[str, Any]:
    execution_request = normalize_execution_request(request)

    if not execution_request:
        return _blocked_result(
            code="invalid_execution_request",
            message="Governed execution request must be a dict.",
            execution_request={},
        )

    if not callable(service):
        return _blocked_result(
            code="service_not_callable",
            message="Governed execution requires an explicit callable service.",
            execution_request=execution_request,
        )

    governance_decision = govern_request_from_dict(execution_request)

    if governance_decision.get("allowed") is not True:
        return _blocked_result(
            code="request_governor_blocked",
            message="Request Governor blocked this execution.",
            execution_request=execution_request,
            governance_decision=governance_decision,
        )

    execution_request["governance_decision"] = governance_decision
    execution_request["context"]["governance_decision"] = governance_decision

    execution_gate = evaluate_execution_gate(execution_request)

    if execution_gate.get("allowed") is not True:
        return _blocked_result(
            code="execution_gate_blocked",
            message="Execution Gate blocked this execution.",
            execution_request=execution_request,
            governance_decision=governance_decision,
            execution_gate=execution_gate,
        )

    execution_request["execution_gate"] = execution_gate
    execution_request["context"]["execution_gate"] = execution_gate

    mutation_guard = evaluate_mutation_guard(execution_request)

    if mutation_guard.get("allowed") is not True:
        return _blocked_result(
            code="mutation_guard_blocked",
            message="Mutation Guard blocked this execution.",
            execution_request=execution_request,
            governance_decision=governance_decision,
            execution_gate=execution_gate,
            mutation_guard=mutation_guard,
        )

    service_context = build_service_context(
        execution_request=execution_request,
        governance_decision=governance_decision,
        execution_gate=execution_gate,
        mutation_guard=mutation_guard,
    )

    try:
        service_result = service(service_context)
    except Exception as exc:
        return {
            "status": "failed",
            "allowed": False,
            "valid": False,
            "executed": False,
            "artifact_type": "northstar_governed_execution_result",
            "governed_execution_version": GOVERNED_EXECUTION_VERSION,
            "checked_at": _utc_now_iso(),
            "error": {
                "code": "service_execution_failed",
                "type": type(exc).__name__,
                "message": str(exc),
            },
            "request": _safe_request_projection(execution_request),
            "stages": {
                "request_governor": governance_decision,
                "execution_gate": execution_gate,
                "mutation_guard": mutation_guard,
                "service": {
                    "status": "failed",
                    "allowed": False,
                    "result": {},
                },
            },
        }

    if not isinstance(service_result, dict):
        service_result = {
            "status": "ok",
            "result": service_result,
        }

    return {
        "status": "ok",
        "allowed": True,
        "valid": True,
        "executed": True,
        "artifact_type": "northstar_governed_execution_result",
        "governed_execution_version": GOVERNED_EXECUTION_VERSION,
        "checked_at": _utc_now_iso(),
        "request": _safe_request_projection(execution_request),
        "stages": {
            "request_governor": governance_decision,
            "execution_gate": execution_gate,
            "mutation_guard": mutation_guard,
            "service": {
                "status": service_result.get("status", "ok"),
                "allowed": True,
                "result": service_result,
            },
        },
        "service_result": service_result,
    }
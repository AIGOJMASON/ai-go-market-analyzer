from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from AI_GO.core.canon_runtime.canon_enforcer import enforce_canon_action_from_dict
from AI_GO.core.execution_gate.runtime_execution_gate import validate_execution_request
from AI_GO.core.state_runtime.state_validator import validate_state_action


REQUEST_GOVERNOR_VERSION = "v1.3"


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


def _bool(value: Any) -> bool:
    return bool(value is True)


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
            "watcher": {
                "status": "not_supplied",
                "allowed": None,
                "decision": {},
            },
            "state": {
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
                "status": "not_run",
                "allowed": False,
                "decision": {},
            },
        },
        "rejection_reasons": [],
        "warnings": [],
        "message": "",
    }


def _reject(result: Dict[str, Any], code: str, message: str) -> None:
    result["rejection_reasons"].append(
        {
            "code": code,
            "message": message,
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


def _build_state_action(request: GovernedRequest) -> Dict[str, Any]:
    return {
        "action_type": request.action_type,
        "action_class": request.action_class,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "payload": dict(request.payload),
        "context": dict(request.context),
    }


def _build_canon_action(request: GovernedRequest) -> Dict[str, Any]:
    context = dict(request.context)

    if request.request_id:
        context.setdefault("request_id", request.request_id)

    if request.child_core_id:
        context.setdefault("child_core_id", request.child_core_id)

    return {
        "action_type": request.action_type,
        "action_class": request.action_class,
        "actor": request.actor,
        "target": request.target,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "route": request.route,
        "payload": dict(request.payload),
        "context": context,
    }


def _build_execution_action(
    *,
    request: GovernedRequest,
    state_decision: Dict[str, Any],
    canon_decision: Dict[str, Any],
) -> Dict[str, Any]:
    context = dict(request.context)
    context["state_decision"] = state_decision
    context["canon_decision"] = canon_decision

    return {
        "action_type": request.action_type,
        "action_class": request.action_class,
        "project_id": request.project_id,
        "phase_id": request.phase_id,
        "payload": dict(request.payload),
        "context": context,
    }


def _record_watcher_stage(request: GovernedRequest, result: Dict[str, Any]) -> None:
    watcher_result = _dict(request.context.get("watcher_result"))

    if not watcher_result:
        return

    result["stages"]["watcher"] = {
        "status": watcher_result.get("status", "unknown"),
        "allowed": _bool(watcher_result.get("valid")),
        "decision": watcher_result,
    }


def _run_state_stage(request: GovernedRequest, result: Dict[str, Any]) -> Dict[str, Any]:
    state_decision = validate_state_action(_build_state_action(request))

    result["stages"]["state"] = {
        "status": state_decision.get("status", "unknown"),
        "allowed": _bool(state_decision.get("allowed")),
        "decision": state_decision,
    }

    return state_decision


def _run_canon_stage(request: GovernedRequest, result: Dict[str, Any]) -> Dict[str, Any]:
    canon_decision = enforce_canon_action_from_dict(_build_canon_action(request))

    result["stages"]["canon"] = {
        "status": canon_decision.get("status", "unknown"),
        "allowed": _bool(canon_decision.get("allowed")),
        "decision": canon_decision,
    }

    return canon_decision


def _run_execution_gate_stage(
    *,
    request: GovernedRequest,
    result: Dict[str, Any],
    state_decision: Dict[str, Any],
    canon_decision: Dict[str, Any],
) -> Dict[str, Any]:
    execution_decision = validate_execution_request(
        _build_execution_action(
            request=request,
            state_decision=state_decision,
            canon_decision=canon_decision,
        )
    )

    result["stages"]["execution_gate"] = {
        "status": execution_decision.get("status", "unknown"),
        "allowed": _bool(execution_decision.get("allowed")),
        "decision": execution_decision,
    }

    return execution_decision


def govern_request(request: GovernedRequest) -> Dict[str, Any]:
    result = _base_decision(request)

    _validate_request_shape(request, result)
    _record_watcher_stage(request, result)

    if result["rejection_reasons"]:
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        result["message"] = "Request blocked before runtime enforcement."
        return result

    state_decision = _run_state_stage(request, result)
    if state_decision.get("allowed") is not True:
        _reject(
            result,
            "state_runtime_blocked",
            "State Runtime blocked this request.",
        )
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        result["message"] = "Request blocked by State Runtime."
        return result

    canon_decision = _run_canon_stage(request, result)
    if canon_decision.get("allowed") is not True:
        result["rejection_reasons"].append(
            {
                "code": "canon_enforcement_blocked",
                "message": "Canon Enforcer blocked this request.",
                "canon_rejection_reasons": canon_decision.get("rejection_reasons", []),
            }
        )
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        result["message"] = "Request blocked by Canon Enforcer."
        return result

    execution_decision = _run_execution_gate_stage(
        request=request,
        result=result,
        state_decision=state_decision,
        canon_decision=canon_decision,
    )
    if execution_decision.get("allowed") is not True:
        _reject(
            result,
            "execution_gate_blocked",
            "Execution Gate blocked this request.",
        )
        result["status"] = "blocked"
        result["decision"] = "block"
        result["allowed"] = False
        result["valid"] = False
        result["message"] = "Request blocked by Execution Gate."
        return result

    result["status"] = "passed"
    result["decision"] = "allow"
    result["allowed"] = True
    result["valid"] = True
    result["message"] = "Request passed root governance checkpoint."

    return result


def govern_request_from_dict(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = build_governed_request_from_dict(payload)
    return govern_request(request)


def assert_request_allowed(payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = govern_request_from_dict(payload)

    if decision.get("allowed") is not True:
        raise PermissionError(decision)

    return decision
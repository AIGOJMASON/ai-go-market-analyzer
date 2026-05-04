from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


EXECUTION_GATE_VERSION = "northstar_6b_execution_gate_v1"

MUTATION_OR_EXECUTION_CLASSES = {
    "write_state",
    "workflow_transition",
    "send_delivery",
    "execute",
}

MUTATION_OR_EXECUTION_TYPES = {
    "phase_closeout",
    "send_phase_closeout",
    "close_phase",
    "record_signoff",
    "complete_signoff",
    "decline_signoff",
    "send_email",
    "send_external",
    "call_external_service",
    "write_receipt",
    "generate_artifact",
    "write_state",
    "mutate_state",
}

FORBIDDEN_EXECUTION_FLAGS = {
    "bypass_execution_gate",
    "bypass_watcher",
    "bypass_state_authority",
    "bypass_request_governor",
    "hidden_state_mutation",
    "governance_override",
    "watcher_override",
    "state_authority_override",
    "canon_override",
    "execution_gate_override",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _bool(value: Any) -> bool:
    return value is True


def _dedupe(values: List[str]) -> List[str]:
    return sorted({_clean(value) for value in values if _clean(value)})


def _base_result(
    *,
    action_type: str,
    action_class: str,
    request_id: str,
    route: str,
    project_id: str,
    phase_id: str,
) -> Dict[str, Any]:
    return {
        "status": "pending",
        "valid": False,
        "allowed": False,
        "decision": "pending",
        "artifact_type": "northstar_execution_gate_decision",
        "execution_gate_version": EXECUTION_GATE_VERSION,
        "checked_at": _utc_now_iso(),
        "request": {
            "request_id": request_id,
            "route": route,
            "action_type": action_type,
            "action_class": action_class,
            "project_id": project_id,
            "phase_id": phase_id,
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
        "Execution gate passed."
        if allowed
        else "Execution gate blocked this action."
    )
    return result


def _stage_decision(governance_decision: Dict[str, Any], stage_name: str) -> Dict[str, Any]:
    stages = _as_dict(governance_decision.get("stages"))
    stage = _as_dict(stages.get(stage_name))
    return _as_dict(stage.get("decision"))


def _stage_allowed(governance_decision: Dict[str, Any], stage_name: str) -> Optional[bool]:
    stages = _as_dict(governance_decision.get("stages"))
    stage = _as_dict(stages.get(stage_name))

    if "allowed" in stage:
        return stage.get("allowed") is True

    decision = _as_dict(stage.get("decision"))
    if decision:
        return decision.get("allowed") is True or decision.get("valid") is True

    return None


def evaluate_execution_gate(execution_request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(execution_request, dict):
        result = _base_result(
            action_type="",
            action_class="",
            request_id="",
            route="",
            project_id="",
            phase_id="",
        )
        _fail(result, "execution_request_must_be_dict")
        return _finalize(result)

    payload = _as_dict(execution_request.get("payload"))
    context = _as_dict(execution_request.get("context"))
    authority = _as_dict(execution_request.get("authority"))
    governance_decision = _as_dict(
        execution_request.get("governance_decision")
        or context.get("governance_decision")
    )

    action_type = _clean(execution_request.get("action_type"))
    action_class = _clean(execution_request.get("action_class"))
    request_id = _clean(execution_request.get("request_id") or context.get("request_id"))
    route = _clean(execution_request.get("route"))
    project_id = _clean(execution_request.get("project_id"))
    phase_id = _clean(execution_request.get("phase_id"))

    result = _base_result(
        action_type=action_type,
        action_class=action_class,
        request_id=request_id,
        route=route,
        project_id=project_id,
        phase_id=phase_id,
    )

    for code, value in {
        "action_type_present": action_type,
        "action_class_present": action_class,
        "actor_present": _clean(execution_request.get("actor")),
        "target_present": _clean(execution_request.get("target")),
        "route_present": route,
    }.items():
        _require(result, code)
        if value:
            _pass(result, code)
        else:
            _fail(result, code)

    is_execution_like = (
        action_class in MUTATION_OR_EXECUTION_CLASSES
        or action_type in MUTATION_OR_EXECUTION_TYPES
    )

    _require(result, "execution_like_action")
    if is_execution_like:
        _pass(result, "execution_like_action")
    else:
        _warn(result, "non_execution_action")
        return _finalize(result)

    _require(result, "request_governor_allowed")
    if governance_decision.get("allowed") is True:
        _pass(result, "request_governor_allowed")
    else:
        _fail(result, "request_governor_not_allowed")

    _require(result, "operator_approved")
    operator_approved = _bool(
        execution_request.get("operator_approved")
        or payload.get("operator_approved")
        or context.get("operator_approved")
        or context.get("approval_granted")
    )
    if operator_approved:
        _pass(result, "operator_approved")
    else:
        _fail(result, "operator_approval_missing")

    _require(result, "receipt_planned_or_present")
    receipt_planned = _bool(
        execution_request.get("receipt_planned")
        or payload.get("receipt_planned")
        or context.get("receipt_planned")
    )
    receipt_present = bool(
        _clean(payload.get("receipt_id"))
        or _clean(payload.get("receipt_path"))
        or _clean(context.get("receipt_id"))
        or _clean(context.get("receipt_path"))
        or _as_list(payload.get("receipt_paths"))
        or _as_list(context.get("receipt_paths"))
    )
    if receipt_planned or receipt_present:
        _pass(result, "receipt_planned_or_present")
    else:
        _fail(result, "receipt_not_planned")

    _require(result, "state_mutation_declared")
    state_mutation_declared = _bool(
        execution_request.get("state_mutation_declared")
        or payload.get("state_mutation_declared")
        or context.get("state_mutation_declared")
    )
    if state_mutation_declared:
        _pass(result, "state_mutation_declared")
    else:
        _fail(result, "state_mutation_not_declared")

    watcher_allowed = _stage_allowed(governance_decision, "watcher")
    if watcher_allowed is not None:
        _require(result, "watcher_stage_allowed")
        if watcher_allowed:
            _pass(result, "watcher_stage_allowed")
        else:
            _fail(result, "watcher_stage_not_allowed")
    else:
        watcher_result = _as_dict(context.get("watcher_result"))
        _require(result, "watcher_result_valid")
        if watcher_result.get("valid") is True or watcher_result.get("allowed") is True:
            _pass(result, "watcher_result_valid")
        else:
            _fail(result, "watcher_result_missing_or_invalid")

    state_allowed = _stage_allowed(governance_decision, "state")
    if state_allowed is not None:
        _require(result, "state_stage_allowed")
        if state_allowed:
            _pass(result, "state_stage_allowed")
        else:
            _fail(result, "state_stage_not_allowed")
    else:
        state_result = _as_dict(context.get("state_result") or context.get("state_decision"))
        if state_result:
            _require(result, "state_result_allowed")
            if state_result.get("allowed") is True or state_result.get("valid") is True:
                _pass(result, "state_result_allowed")
            else:
                _fail(result, "state_result_not_allowed")
        else:
            _warn(result, "state_result_not_supplied")

    canon_allowed = _stage_allowed(governance_decision, "canon")
    if canon_allowed is not None:
        _require(result, "canon_stage_allowed")
        if canon_allowed:
            _pass(result, "canon_stage_allowed")
        else:
            _fail(result, "canon_stage_not_allowed")
    else:
        canon_decision = _as_dict(context.get("canon_decision"))
        if canon_decision:
            _require(result, "canon_decision_allowed")
            if canon_decision.get("allowed") is True or canon_decision.get("valid") is True:
                _pass(result, "canon_decision_allowed")
            else:
                _fail(result, "canon_decision_not_allowed")
        else:
            _warn(result, "canon_decision_not_supplied")

    _require(result, "no_forbidden_execution_flags")
    forbidden_hits = [
        key for key in FORBIDDEN_EXECUTION_FLAGS
        if authority.get(key) is True or context.get(key) is True or payload.get(key) is True
    ]
    if forbidden_hits:
        for hit in forbidden_hits:
            _fail(result, f"forbidden_flag_{hit}")
    else:
        _pass(result, "no_forbidden_execution_flags")

    return _finalize(result)
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from AI_GO.core.canon_runtime.canon_validator import validate_canon_runtime


CANON_ENFORCER_VERSION = "v1.2"

ACTION_CLASSES = {
    "read": {
        "mutates_state": False,
        "requires_operator_approval": False,
        "requires_receipt": False,
        "requires_watcher": False,
    },
    "propose": {
        "mutates_state": False,
        "requires_operator_approval": False,
        "requires_receipt": True,
        "requires_watcher": True,
    },
    "write_state": {
        "mutates_state": True,
        "requires_operator_approval": True,
        "requires_receipt": True,
        "requires_watcher": True,
    },
    "workflow_transition": {
        "mutates_state": True,
        "requires_operator_approval": True,
        "requires_receipt": True,
        "requires_watcher": True,
    },
    "send_delivery": {
        "mutates_state": True,
        "requires_operator_approval": True,
        "requires_receipt": True,
        "requires_watcher": True,
    },
    "execute": {
        "mutates_state": True,
        "requires_operator_approval": True,
        "requires_receipt": True,
        "requires_watcher": True,
    },
}

BLOCKED_ACTION_TYPES = {
    "autonomous_agent",
    "self_modify",
    "direct_execution",
    "bypass_execution_gate",
    "hidden_state_mutation",
    "unbounded_external_integration",
}


@dataclass(frozen=True)
class CanonAction:
    action_type: str
    action_class: str
    actor: str = "unknown"
    target: str = ""
    project_id: str = ""
    phase_id: str = ""
    route: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    return value is True


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _base_result(action: CanonAction) -> Dict[str, Any]:
    return {
        "status": "pending",
        "valid": False,
        "allowed": False,
        "enforcer_version": CANON_ENFORCER_VERSION,
        "checked_at": _utc_now_iso(),
        "action": {
            "action_type": action.action_type,
            "action_class": action.action_class,
            "actor": action.actor,
            "target": action.target,
            "project_id": action.project_id,
            "phase_id": action.phase_id,
            "route": action.route,
        },
        "rejection_reasons": [],
        "warnings": [],
        "required_conditions": [],
        "passed_conditions": [],
        "failed_conditions": [],
        "canon_validation": {},
    }


def _reject(result: Dict[str, Any], code: str, message: str) -> None:
    result["rejection_reasons"].append({"code": code, "message": message})
    result["failed_conditions"].append(code)


def _pass(result: Dict[str, Any], code: str) -> None:
    result["passed_conditions"].append(code)


def _require(result: Dict[str, Any], code: str) -> None:
    result["required_conditions"].append(code)


def _warn(result: Dict[str, Any], code: str, message: str) -> None:
    result["warnings"].append({"code": code, "message": message})


def build_canon_action(
    *,
    action_type: str,
    action_class: str,
    actor: str = "unknown",
    target: str = "",
    project_id: str = "",
    phase_id: str = "",
    route: str = "",
    payload: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> CanonAction:
    return CanonAction(
        action_type=_clean(action_type),
        action_class=_clean(action_class),
        actor=_clean(actor) or "unknown",
        target=_clean(target),
        project_id=_clean(project_id),
        phase_id=_clean(phase_id),
        route=_clean(route),
        payload=dict(payload or {}),
        context=dict(context or {}),
    )


def _validate_canon_runtime_available(result: Dict[str, Any]) -> None:
    _require(result, "canon_runtime_valid")

    validation = validate_canon_runtime()
    result["canon_validation"] = validation

    if validation.get("valid") is True:
        _pass(result, "canon_runtime_valid")
        return

    _reject(
        result,
        "canon_runtime_invalid",
        "Canon runtime validation failed. No governed action may proceed.",
    )


def _validate_action_identity(action: CanonAction, result: Dict[str, Any]) -> None:
    _require(result, "action_type_present")
    _require(result, "action_class_present")
    _require(result, "actor_present")

    if action.action_type:
        _pass(result, "action_type_present")
    else:
        _reject(result, "missing_action_type", "action_type is required.")

    if action.action_class:
        _pass(result, "action_class_present")
    else:
        _reject(result, "missing_action_class", "action_class is required.")

    if action.actor and action.actor != "unknown":
        _pass(result, "actor_present")
    else:
        _reject(result, "missing_actor", "actor is required for canon enforcement.")


def _validate_action_class(action: CanonAction, result: Dict[str, Any]) -> Dict[str, Any]:
    _require(result, "known_action_class")

    action_policy = ACTION_CLASSES.get(action.action_class)
    if action_policy is None:
        _reject(result, "unknown_action_class", f"Unknown action_class: {action.action_class}")
        return {}

    _pass(result, "known_action_class")
    return dict(action_policy)


def _validate_hard_blocks(action: CanonAction, result: Dict[str, Any]) -> None:
    _require(result, "no_hard_blocked_action_type")

    if action.action_type in BLOCKED_ACTION_TYPES:
        _reject(
            result,
            "hard_blocked_action_type",
            f"Action type is blocked during hardening phase: {action.action_type}",
        )
        return

    _pass(result, "no_hard_blocked_action_type")


def _validate_no_direct_execution(action: CanonAction, result: Dict[str, Any]) -> None:
    _require(result, "no_direct_execution")

    route = action.route.lower()
    execution_gate_passed = _bool(
        action.context.get("execution_gate_passed")
        or action.payload.get("execution_gate_passed")
    )

    looks_like_direct_execution = (
        action.action_type in {"execute", "direct_execute"}
        or action.action_class == "execute"
        or "execute" in route
        or "dispatch" in route
    )

    if looks_like_direct_execution and not execution_gate_passed:
        _reject(
            result,
            "execution_gate_required",
            "Execution-like actions require execution_gate_passed=true.",
        )
        return

    _pass(result, "no_direct_execution")


def _validate_watcher_requirement(
    action_policy: Dict[str, Any],
    action: CanonAction,
    result: Dict[str, Any],
) -> None:
    if not action_policy.get("requires_watcher"):
        return

    _require(result, "watcher_passed")

    watcher_passed = _bool(
        action.context.get("watcher_passed")
        or action.payload.get("watcher_passed")
        or _dict(action.context.get("watcher_result")).get("valid")
        or _dict(action.context.get("watcher_result")).get("allowed")
        or _dict(action.payload.get("watcher_result")).get("valid")
        or _dict(action.payload.get("watcher_result")).get("allowed")
    )

    if watcher_passed:
        _pass(result, "watcher_passed")
        return

    _reject(
        result,
        "watcher_required",
        "This action requires a passed watcher result before canon approval.",
    )


def _validate_receipt_requirement(
    action_policy: Dict[str, Any],
    action: CanonAction,
    result: Dict[str, Any],
) -> None:
    if not action_policy.get("requires_receipt"):
        return

    _require(result, "receipt_required")

    receipt_id = _clean(
        action.context.get("receipt_id")
        or action.payload.get("receipt_id")
        or action.context.get("receipt_path")
        or action.payload.get("receipt_path")
    )
    receipt_paths = _list(action.context.get("receipt_paths")) or _list(action.payload.get("receipt_paths"))
    receipt_planned = _bool(action.context.get("receipt_planned") or action.payload.get("receipt_planned"))

    if receipt_id or receipt_paths or receipt_planned:
        _pass(result, "receipt_required")
        return

    _reject(
        result,
        "receipt_missing",
        "This action requires a receipt id, receipt path, receipt_paths entry, or receipt_planned=true.",
    )


def _validate_operator_approval_requirement(
    action_policy: Dict[str, Any],
    action: CanonAction,
    result: Dict[str, Any],
) -> None:
    if not action_policy.get("requires_operator_approval"):
        return

    _require(result, "operator_approval_required")

    approved = _bool(
        action.context.get("operator_approved")
        or action.payload.get("operator_approved")
        or action.context.get("approval_granted")
        or action.payload.get("approval_granted")
    )

    approval_required = action.context.get("approval_required")
    if approval_required is False:
        _reject(
            result,
            "approval_required_cannot_be_false",
            "Mutating or execution actions may not disable approval_required.",
        )
        return

    if approved:
        _pass(result, "operator_approval_required")
        return

    _reject(
        result,
        "operator_approval_missing",
        "This action requires explicit operator approval.",
    )


def _validate_state_mutation_visibility(
    action_policy: Dict[str, Any],
    action: CanonAction,
    result: Dict[str, Any],
) -> None:
    if not action_policy.get("mutates_state"):
        return

    _require(result, "state_mutation_declared")

    mutation_declared = _bool(
        action.context.get("state_mutation_declared")
        or action.payload.get("state_mutation_declared")
        or action.context.get("mutation_declared")
        or action.payload.get("mutation_declared")
    )

    if mutation_declared:
        _pass(result, "state_mutation_declared")
        return

    _reject(
        result,
        "state_mutation_not_declared",
        "State-mutating actions must explicitly declare state_mutation_declared=true.",
    )


def _validate_workflow_requirements(action: CanonAction, result: Dict[str, Any]) -> None:
    if action.action_class != "workflow_transition":
        return

    _require(result, "workflow_context_present")

    workflow_state = _dict(action.context.get("workflow_state")) or _dict(action.payload.get("workflow_state"))
    if not workflow_state:
        _reject(result, "workflow_context_missing", "Workflow transitions require workflow_state context.")
        return

    _pass(result, "workflow_context_present")

    if action.project_id:
        _pass(result, "project_id_present")
    else:
        _reject(result, "project_id_missing", "Workflow transitions require project_id.")

    if action.phase_id:
        _pass(result, "phase_id_present")
    else:
        _reject(result, "phase_id_missing", "Workflow transitions require phase_id.")


def _validate_phase_closeout_requirements(action: CanonAction, result: Dict[str, Any]) -> None:
    if action.action_type not in {"phase_closeout", "send_phase_closeout", "close_phase"}:
        return

    _require(result, "phase_closeout_checklist_ready")
    _require(result, "phase_closeout_signoff_posture")

    checklist_summary = _dict(action.context.get("checklist_summary")) or _dict(action.payload.get("checklist_summary"))
    workflow_state = _dict(action.context.get("workflow_state")) or _dict(action.payload.get("workflow_state"))
    phase_instance = _dict(action.context.get("phase_instance")) or _dict(action.payload.get("phase_instance"))

    ready_for_signoff = _bool(checklist_summary.get("ready_for_signoff"))
    phase_status = _clean(phase_instance.get("phase_status"))
    current_phase_id = _clean(workflow_state.get("current_phase_id"))

    if ready_for_signoff:
        _pass(result, "phase_closeout_checklist_ready")
    else:
        _reject(
            result,
            "checklist_not_ready",
            "Phase closeout is blocked because checklist_summary.ready_for_signoff is not true.",
        )

    if phase_status == "awaiting_signoff":
        _pass(result, "phase_closeout_signoff_posture")
    else:
        _reject(
            result,
            "phase_not_awaiting_signoff",
            "Phase closeout is blocked unless phase_status is awaiting_signoff.",
        )

    if action.phase_id and current_phase_id and action.phase_id != current_phase_id:
        _reject(
            result,
            "phase_not_current",
            "Phase closeout is blocked because requested phase_id is not the canonical current_phase_id.",
        )


def _validate_delivery_requirements(action: CanonAction, result: Dict[str, Any]) -> None:
    if action.action_class != "send_delivery":
        return

    _require(result, "delivery_target_present")

    recipient = _clean(
        action.payload.get("recipient")
        or action.payload.get("client_email")
        or action.context.get("recipient")
        or action.context.get("client_email")
    )

    if recipient:
        _pass(result, "delivery_target_present")
    else:
        _reject(result, "delivery_target_missing", "Delivery actions require recipient or client_email.")


def _enforce_canon_action(action: CanonAction) -> Dict[str, Any]:
    result = _base_result(action)

    try:
        _validate_canon_runtime_available(result)
        _validate_action_identity(action, result)
        action_policy = _validate_action_class(action, result)
        _validate_hard_blocks(action, result)
        _validate_no_direct_execution(action, result)

        if action_policy:
            _validate_watcher_requirement(action_policy, action, result)
            _validate_receipt_requirement(action_policy, action, result)
            _validate_operator_approval_requirement(action_policy, action, result)
            _validate_state_mutation_visibility(action_policy, action, result)

        _validate_workflow_requirements(action, result)
        _validate_phase_closeout_requirements(action, result)
        _validate_delivery_requirements(action, result)

    except Exception as exc:
        _reject(
            result,
            "canon_enforcer_exception",
            f"Canon enforcer failed closed: {type(exc).__name__}: {exc}",
        )

    allowed = len(result["rejection_reasons"]) == 0
    result["allowed"] = allowed
    result["valid"] = allowed
    result["status"] = "passed" if allowed else "blocked"
    result["decision"] = "allow" if allowed else "block"
    result["message"] = (
        "Canon pass granted for bounded governed action."
        if allowed
        else "NO ACTION EXECUTES WITHOUT CANON PASS."
    )
    return result


def enforce_canon_action_from_dict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Canonical public entrypoint.

    All route/API/governor callers should use this function.
    It normalizes plain dictionaries into CanonAction and then passes through
    the single private engine `_enforce_canon_action`.
    """

    if not isinstance(payload, dict):
        action = build_canon_action(action_type="invalid", action_class="invalid", actor="unknown")
        result = _base_result(action)
        _reject(result, "invalid_payload", "Canon enforcement payload must be a dict.")
        result["status"] = "blocked"
        result["decision"] = "block"
        result["message"] = "NO ACTION EXECUTES WITHOUT CANON PASS."
        return result

    action = build_canon_action(
        action_type=payload.get("action_type", ""),
        action_class=payload.get("action_class", ""),
        actor=payload.get("actor", "unknown"),
        target=payload.get("target", ""),
        project_id=payload.get("project_id", ""),
        phase_id=payload.get("phase_id", ""),
        route=payload.get("route", ""),
        payload=_dict(payload.get("payload")),
        context=_dict(payload.get("context")),
    )
    return _enforce_canon_action(action)


def enforce_canon_action(action: CanonAction) -> Dict[str, Any]:
    """
    Compatibility shim for typed internal callers only.

    Dict callers must use enforce_canon_action_from_dict.
    This fails closed for dicts so the legacy flat-dict implementation cannot
    silently reappear.
    """

    if isinstance(action, dict):
        result = enforce_canon_action_from_dict(
            {
                "action_type": "",
                "action_class": "",
                "actor": "unknown",
                "payload": {},
                "context": {},
            }
        )
        _reject(
            result,
            "legacy_dict_entrypoint_blocked",
            "Dict callers must use enforce_canon_action_from_dict.",
        )
        result["allowed"] = False
        result["valid"] = False
        result["status"] = "blocked"
        result["decision"] = "block"
        result["message"] = "Legacy dict canon entrypoint blocked."
        return result

    return _enforce_canon_action(action)


def assert_canon_allowed(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = enforce_canon_action_from_dict(payload)
    if result.get("allowed") is not True:
        raise PermissionError(result)
    return result


def assert_canon_pass(payload: Dict[str, Any]) -> Dict[str, Any]:
    return assert_canon_allowed(payload)
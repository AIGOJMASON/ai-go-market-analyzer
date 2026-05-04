from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


ROOT_WATCHER_VERSION = "root_watcher_v1.0"


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


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _dedupe(values: List[str]) -> List[str]:
    return sorted({str(value or "").strip() for value in values if str(value or "").strip()})


def _base_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_type": "root_watcher_decision",
        "artifact_version": ROOT_WATCHER_VERSION,
        "checked_at": _utc_now_iso(),
        "source": "AI_GO.core.watcher.root_watcher",
        "status": "pending",
        "valid": False,
        "allowed": False,
        "profile": _clean(payload.get("watcher_profile")) or "root",
        "action": {
            "action_type": _clean(payload.get("action_type")),
            "action_class": _clean(payload.get("action_class")),
            "route": _clean(payload.get("route")),
            "target": _clean(payload.get("target")),
            "project_id": _clean(payload.get("project_id")),
            "phase_id": _clean(payload.get("phase_id")),
        },
        "errors": [],
        "warnings": [],
        "passed_conditions": [],
        "failed_conditions": [],
        "supplied_watcher_result": _dict(payload.get("supplied_watcher_result")),
    }


def _pass(result: Dict[str, Any], code: str) -> None:
    result["passed_conditions"].append(code)


def _warn(result: Dict[str, Any], code: str) -> None:
    result["warnings"].append(code)


def _fail(result: Dict[str, Any], code: str) -> None:
    result["errors"].append(code)
    result["failed_conditions"].append(code)


def _finalize(result: Dict[str, Any]) -> Dict[str, Any]:
    result["errors"] = _dedupe(result["errors"])
    result["warnings"] = _dedupe(result["warnings"])
    result["passed_conditions"] = _dedupe(result["passed_conditions"])
    result["failed_conditions"] = _dedupe(result["failed_conditions"])

    allowed = len(result["errors"]) == 0
    result["allowed"] = allowed
    result["valid"] = allowed
    result["status"] = "passed" if allowed else "blocked"
    result["message"] = (
        "Root watcher passed."
        if allowed
        else "Root watcher blocked this request."
    )
    return result


def _requires_watcher(payload: Dict[str, Any]) -> bool:
    if payload.get("watcher_required") is True:
        return True

    if payload.get("execution_intent") is True:
        return True

    action_class = _clean(payload.get("action_class"))
    action_type = _clean(payload.get("action_type"))

    return action_class in MUTATION_OR_EXECUTION_CLASSES or action_type in MUTATION_OR_EXECUTION_TYPES


def _validate_supplied_watcher(payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    supplied = _dict(payload.get("supplied_watcher_result"))
    if not supplied:
        _warn(result, "no_route_supplied_watcher_result")
        return

    supplied_passed = supplied.get("valid") is True or supplied.get("allowed") is True
    if supplied_passed:
        _pass(result, "route_supplied_watcher_passed")
        return

    _fail(result, "route_supplied_watcher_failed")


def _validate_common_shape(payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    if _clean(payload.get("action_type")):
        _pass(result, "action_type_present")
    else:
        _fail(result, "missing_action_type")

    if _clean(payload.get("action_class")):
        _pass(result, "action_class_present")
    else:
        _fail(result, "missing_action_class")

    if _clean(payload.get("actor")) and _clean(payload.get("actor")) != "unknown":
        _pass(result, "actor_present")
    else:
        _fail(result, "missing_actor")

    if _clean(payload.get("route")):
        _pass(result, "route_present")
    else:
        _warn(result, "missing_route")

    if _clean(payload.get("target")):
        _pass(result, "target_present")
    else:
        _warn(result, "missing_target")


def _validate_no_bypass(payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    blocked_flags = {
        "bypass_watcher": payload.get("bypass_watcher") is True,
        "bypass_execution_gate": payload.get("bypass_execution_gate") is True,
        "hidden_state_mutation": payload.get("hidden_state_mutation") is True,
        "watcher_override": payload.get("watcher_override") is True,
        "governance_override": payload.get("governance_override") is True,
    }

    for flag_name, active in blocked_flags.items():
        if active:
            _fail(result, flag_name)
        else:
            _pass(result, f"no_{flag_name}")


def _validate_mutation_posture(payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    if not _requires_watcher(payload):
        _pass(result, "watcher_not_required_for_read_only_action")
        return

    _pass(result, "watcher_required_for_mutation_or_execution")

    if payload.get("state_authority_passed") is True or payload.get("state_passed") is True:
        _pass(result, "state_authority_passed")
    else:
        _fail(result, "state_authority_not_passed")

    if payload.get("state_mutation_declared") is True or payload.get("mutation_declared") is True:
        _pass(result, "state_mutation_declared")
    else:
        _fail(result, "state_mutation_not_declared")

    if payload.get("receipt_planned") is True or _clean(payload.get("receipt_id")) or _clean(payload.get("receipt_path")):
        _pass(result, "receipt_planned")
    else:
        _fail(result, "receipt_not_planned")


def _validate_phase_closeout(payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    action_type = _clean(payload.get("action_type"))
    action_class = _clean(payload.get("action_class"))

    if action_type not in {"phase_closeout", "send_phase_closeout", "close_phase"} and action_class != "workflow_transition":
        return

    workflow_state = _dict(payload.get("workflow_state"))
    phase_instance = _dict(payload.get("phase_instance"))
    checklist_summary = _dict(payload.get("checklist_summary"))
    change_closeout_guard = _dict(payload.get("change_closeout_guard"))

    current_phase_id = _clean(workflow_state.get("current_phase_id"))
    requested_phase_id = _clean(payload.get("phase_id"))
    phase_status = _clean(phase_instance.get("phase_status"))

    if current_phase_id:
        _pass(result, "current_phase_id_present")
    else:
        _fail(result, "current_phase_id_missing")

    if requested_phase_id:
        _pass(result, "requested_phase_id_present")
    else:
        _fail(result, "requested_phase_id_missing")

    if current_phase_id and requested_phase_id and current_phase_id == requested_phase_id:
        _pass(result, "requested_phase_is_current")
    elif current_phase_id and requested_phase_id:
        _fail(result, "requested_phase_not_current")

    if phase_status == "awaiting_signoff":
        _pass(result, "phase_awaiting_signoff")
    else:
        _fail(result, "phase_not_awaiting_signoff")

    if checklist_summary.get("ready_for_signoff") is True:
        _pass(result, "checklist_ready_for_signoff")
    else:
        _fail(result, "checklist_not_ready_for_signoff")

    if change_closeout_guard.get("phase_has_blocking_unresolved_changes") is True:
        _fail(result, "blocking_unresolved_change_exists")
    else:
        _pass(result, "no_blocking_unresolved_changes")


def evaluate_root_watcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    source = _dict(payload)
    result = _base_result(source)

    _validate_common_shape(source, result)
    _validate_no_bypass(source, result)
    _validate_supplied_watcher(source, result)
    _validate_mutation_posture(source, result)
    _validate_phase_closeout(source, result)

    return _finalize(result)


def assert_root_watcher_pass(payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = evaluate_root_watcher(payload)

    if decision.get("allowed") is not True:
        raise PermissionError(
            {
                "error": "root_watcher_blocked",
                "decision": decision,
            }
        )

    return decision
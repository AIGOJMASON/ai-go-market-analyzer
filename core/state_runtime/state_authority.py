from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from AI_GO.core.state_runtime.state_paths import (
    PathDriftViolation,
    contractor_project_root,
)
from AI_GO.core.state_runtime.state_reader import (
    find_phase_instance,
    read_contractor_project_state,
)


STATE_AUTHORITY_VERSION = "v1.4"

GOVERNED_PERSISTENCE_ENVELOPE = "governed_persistence_envelope"

STATE_REQUIRED_ACTION_CLASSES = {
    "write_state",
    "workflow_transition",
    "send_delivery",
    "execute",
}

STATE_REQUIRED_ACTION_TYPES = {
    "mutate_state",
    "write_state",
    "advance_workflow",
    "close_phase",
    "record_signoff",
    "complete_signoff",
    "decline_signoff",
    "send_phase_closeout",
    "phase_closeout",
    "workflow_initialize",
    "workflow_checklist_upsert",
    "workflow_reconcile",
    "workflow_repair_upsert",
    "workflow_signoff_status_update",
}

FORBIDDEN_AUTHORITY_TRUE = {
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_dispatch",
    "execution_allowed",
    "mutation_allowed",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_bool(value: Any) -> bool:
    return value is True


def _dedupe(values: List[str]) -> List[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _unwrap_governed_payload(value: Any) -> Any:
    if (
        isinstance(value, dict)
        and value.get("artifact_type") == GOVERNED_PERSISTENCE_ENVELOPE
        and "payload" in value
    ):
        return value.get("payload")

    return value


def _load_json(path: Path) -> Any:
    if not path.exists():
        return {} if path.suffix == ".json" else []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if path.suffix == ".json" else []

    return _unwrap_governed_payload(payload)


def _project_root(project_id: str) -> Path:
    return contractor_project_root(project_id)


def _load_project_state(project_id: str) -> Dict[str, Any]:
    try:
        return read_contractor_project_state(project_id)
    except Exception:
        return {}


def _load_workflow_state(project_id: str) -> Dict[str, Any]:
    project_state = _load_project_state(project_id)
    workflow_state = project_state.get("workflow_state")
    return _safe_dict(workflow_state)


def _normalize_phase_instances(payload: Any) -> List[Dict[str, Any]]:
    payload = _unwrap_governed_payload(payload)

    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        phase_instances = _unwrap_governed_payload(payload.get("phase_instances", []))
        if isinstance(phase_instances, list):
            return [dict(item) for item in phase_instances if isinstance(item, dict)]

    return []


def _load_phase_instances(project_id: str) -> List[Dict[str, Any]]:
    project_state = _load_project_state(project_id)
    phase_instances = project_state.get("phase_instances")
    if isinstance(phase_instances, list):
        return [dict(item) for item in phase_instances if isinstance(item, dict)]

    root = _project_root(project_id)
    payload = _load_json(root / "workflow" / "phase_instances.json")
    return _normalize_phase_instances(payload)


def _authority_block() -> Dict[str, Any]:
    return {
        "mode": "state_verification_only",
        "read_only": True,
        "can_verify_state": True,
        "can_execute": False,
        "can_mutate_state": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_create_decision": False,
        "can_dispatch": False,
        "execution_allowed": False,
        "mutation_allowed": False,
    }


def _use_policy_block() -> Dict[str, Any]:
    return {
        "request_governor_may_read": True,
        "canon_may_receive_state_pass": True,
        "watcher_may_compare": True,
        "operator_may_read": True,
        "may_change_state": False,
        "may_execute": False,
        "may_dispatch": False,
        "may_override_governance": False,
        "may_override_watcher": False,
        "may_override_execution_gate": False,
    }


def _is_state_required(action_type: str, action_class: str) -> bool:
    return (
        action_type in STATE_REQUIRED_ACTION_TYPES
        or action_class in STATE_REQUIRED_ACTION_CLASSES
    )


def _find_authority_violations(packet: Dict[str, Any]) -> List[str]:
    violations: List[str] = []

    authority = _safe_dict(packet.get("authority"))
    for key in FORBIDDEN_AUTHORITY_TRUE:
        if authority.get(key) is True:
            violations.append(f"authority.{key}")

    use_policy = _safe_dict(packet.get("use_policy"))
    for key in (
        "may_change_state",
        "may_execute",
        "may_dispatch",
        "may_override_governance",
        "may_override_watcher",
        "may_override_execution_gate",
    ):
        if use_policy.get(key) is True:
            violations.append(f"use_policy.{key}")

    return violations


def _load_validator(name: str) -> Optional[Callable[..., Dict[str, Any]]]:
    for module_name in (
        "AI_GO.core.state_runtime.state_validator",
        "AI_GO.core.state_runtime.contractor_state_profiles",
    ):
        try:
            module = __import__(module_name, fromlist=[name])
            candidate = getattr(module, name, None)
            if callable(candidate):
                return candidate
        except Exception:
            continue

    return None


def _fallback_validate_workflow_state(
    *,
    project_id: str,
    phase_id: str,
    action: str,
    candidate_phase_instances: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)
    clean_action = _safe_str(action)

    project_state = _load_project_state(clean_project_id)
    workflow_state = _safe_dict(project_state.get("workflow_state"))
    phase_instances = _safe_list(project_state.get("phase_instances"))
    candidate_phase_instances = (
        candidate_phase_instances if isinstance(candidate_phase_instances, list) else []
    )

    checks["project_exists"] = project_state.get("project_exists") is True
    checks["workflow_state_exists"] = bool(workflow_state)
    checks["phase_instance_count"] = len(phase_instances)
    checks["candidate_phase_instance_count"] = len(candidate_phase_instances)
    checks["action"] = clean_action

    if not checks["project_exists"]:
        errors.append("project_not_found")

    matched_phase: Dict[str, Any] = {}
    if clean_phase_id:
        matched_phase = find_phase_instance(
            project_state=project_state,
            phase_id=clean_phase_id,
        )
        checks["phase_id"] = clean_phase_id
        checks["phase_instance_exists"] = bool(matched_phase)

        if not matched_phase and clean_action not in {"workflow_initialize"}:
            errors.append("phase_instance_missing")

    if clean_action == "workflow_initialize":
        if not candidate_phase_instances:
            errors.append("candidate_phase_instances_missing")

    elif clean_action == "workflow_checklist_upsert":
        if not clean_phase_id:
            errors.append("phase_id_missing")

    elif clean_action == "workflow_legacy_signoff_record":
        if not clean_phase_id:
            errors.append("phase_id_missing")

    elif clean_action == "workflow_signoff_status_update":
        if not clean_phase_id:
            errors.append("phase_id_missing")

    elif clean_action == "workflow_reconcile":
        if not workflow_state:
            errors.append("workflow_state_missing")

    elif clean_action == "workflow_repair_upsert":
        if not candidate_phase_instances:
            errors.append("candidate_phase_instances_missing")

    else:
        errors.append("unknown_workflow_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_workflow",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "decision": "allow" if valid else "block",
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "action": clean_action,
        "checks": checks,
        "errors": _dedupe(errors),
        "warnings": [],
        "matched_phase": matched_phase,
        "state_context": {
            "workflow_state": workflow_state,
            "phase_instances_count": len(phase_instances),
            "project_root": project_state.get("project_root", ""),
        },
        "sealed": True,
    }


def _call_validate_state_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    validator = _load_validator("validate_state_action")
    if validator is None:
        action_type = _safe_str(payload.get("action_type"))
        if action_type.startswith("workflow_"):
            return _fallback_validate_workflow_state(
                project_id=_safe_str(payload.get("project_id")),
                phase_id=_safe_str(payload.get("phase_id")),
                action=action_type,
                candidate_phase_instances=_safe_list(
                    _safe_dict(payload.get("context")).get("candidate_phase_instances")
                )
                or _safe_list(
                    _safe_dict(payload.get("payload")).get("candidate_phase_instances")
                ),
            )

        return {
            "status": "unavailable",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": ["validate_state_action_unavailable"],
            "warnings": [],
            "state_context": {},
            "sealed": True,
        }

    try:
        result = _safe_dict(validator(payload))
        if "allowed" not in result:
            result["allowed"] = result.get("valid") is True
        if "decision" not in result:
            result["decision"] = "allow" if result.get("allowed") is True else "block"
        return result
    except Exception as exc:
        return {
            "status": "failed",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": [f"validate_state_action_exception:{type(exc).__name__}:{exc}"],
            "warnings": [],
            "state_context": {},
            "sealed": True,
        }


def _call_validate_contractor_workflow_state(
    *,
    project_id: str,
    phase_id: str,
    action: str,
    payload: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_phase_instances = _safe_list(context.get("candidate_phase_instances")) or _safe_list(
        payload.get("candidate_phase_instances")
    )

    validator = _load_validator("validate_contractor_workflow_state")
    if validator is None:
        return _fallback_validate_workflow_state(
            project_id=project_id,
            phase_id=phase_id,
            action=action,
            candidate_phase_instances=candidate_phase_instances,
        )

    try:
        project_root = _project_root(project_id)
        workflow_state = _load_workflow_state(project_id)
        phase_instances = _load_phase_instances(project_id)
    except (ValueError, PathDriftViolation) as exc:
        return {
            "status": "blocked",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": [f"path_integrity_failed:{type(exc).__name__}:{exc}"],
            "warnings": [],
            "state_context": {},
            "sealed": True,
        }

    try:
        result = validator(
            project_id=project_id,
            action=action,
            workflow_state=workflow_state,
            phase_instances=phase_instances,
            phase_id=phase_id,
            candidate_phase_instances=candidate_phase_instances,
        )
        result = _safe_dict(result)

        if "allowed" not in result:
            result["allowed"] = result.get("valid") is True

        if "decision" not in result:
            result["decision"] = "allow" if result.get("allowed") is True else "block"

        result.setdefault(
            "state_context",
            {
                "workflow_state": workflow_state,
                "phase_instances_count": len(phase_instances),
                "project_root": str(project_root),
            },
        )
        return result

    except Exception as exc:
        return {
            "status": "failed",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": [
                f"validate_contractor_workflow_state_exception:{type(exc).__name__}:{exc}"
            ],
            "warnings": [],
            "state_context": {
                "workflow_state": workflow_state,
                "phase_instances_count": len(phase_instances),
                "project_root": str(project_root),
            },
            "sealed": True,
        }


def _call_validate_contractor_phase_state(
    *,
    project_id: str,
    phase_id: str,
) -> Dict[str, Any]:
    validator = _load_validator("validate_contractor_phase_state")
    if validator is None:
        return {
            "status": "unavailable",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": ["validate_contractor_phase_state_unavailable"],
            "warnings": [],
            "state_context": {},
            "sealed": True,
        }

    try:
        project_root = _project_root(project_id)
        workflow_state = _load_workflow_state(project_id)
        phase_instances = _load_phase_instances(project_id)
    except (ValueError, PathDriftViolation) as exc:
        return {
            "status": "blocked",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": [f"path_integrity_failed:{type(exc).__name__}:{exc}"],
            "warnings": [],
            "state_context": {},
            "sealed": True,
        }

    try:
        result = validator(
            project_id=project_id,
            phase_id=phase_id,
            workflow_state=workflow_state,
            phase_instances=phase_instances,
        )
        result = _safe_dict(result)

        if "allowed" not in result:
            result["allowed"] = result.get("valid") is True

        if "decision" not in result:
            result["decision"] = "allow" if result.get("allowed") is True else "block"

        result.setdefault(
            "state_context",
            {
                "workflow_state": workflow_state,
                "phase_instances_count": len(phase_instances),
                "project_root": str(project_root),
            },
        )
        return result

    except Exception as exc:
        return {
            "status": "failed",
            "valid": False,
            "allowed": False,
            "decision": "block",
            "errors": [
                f"validate_contractor_phase_state_exception:{type(exc).__name__}:{exc}"
            ],
            "warnings": [],
            "state_context": {
                "workflow_state": workflow_state,
                "phase_instances_count": len(phase_instances),
                "project_root": str(project_root),
            },
            "sealed": True,
        }


def _run_state_validation(
    *,
    action_type: str,
    action_class: str,
    project_id: str,
    phase_id: str,
    payload: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    if action_type.startswith("workflow_"):
        return _call_validate_contractor_workflow_state(
            project_id=project_id,
            phase_id=phase_id,
            action=action_type,
            payload=payload,
            context=context,
        )

    if action_type in {"phase_closeout", "send_phase_closeout", "close_phase"}:
        phase_result = _call_validate_contractor_phase_state(
            project_id=project_id,
            phase_id=phase_id,
        )

        if phase_result.get("status") != "unavailable":
            return phase_result

    return _call_validate_state_action(
        {
            "action_type": action_type,
            "action_class": action_class,
            "project_id": project_id,
            "phase_id": phase_id,
            "payload": payload,
            "context": context,
        }
    )


def build_state_authority_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(payload)

    action_type = _safe_str(source.get("action_type"))
    action_class = _safe_str(source.get("action_class"))
    project_id = _safe_str(source.get("project_id"))
    phase_id = _safe_str(source.get("phase_id"))

    errors: List[str] = []
    warnings: List[str] = []

    state_required = _is_state_required(
        action_type=action_type,
        action_class=action_class,
    )

    state_validation: Dict[str, Any] = {}

    if not action_type:
        errors.append("action_type_missing")

    if not action_class:
        errors.append("action_class_missing")

    if state_required and not project_id:
        errors.append("state_required_project_id_missing")

    if state_required and not errors:
        state_validation = _run_state_validation(
            action_type=action_type,
            action_class=action_class,
            project_id=project_id,
            phase_id=phase_id,
            payload=_safe_dict(source.get("payload")),
            context=_safe_dict(source.get("context")),
        )

        if (
            state_validation.get("valid") is not True
            and state_validation.get("allowed") is not True
        ):
            errors.append("state_runtime_validation_failed")

    if not state_required:
        warnings.append("state_validation_not_required_for_action")

    packet: Dict[str, Any] = {
        "status": "pending",
        "artifact_type": "state_authority_packet",
        "artifact_version": STATE_AUTHORITY_VERSION,
        "generated_at": _utc_now_iso(),
        "sealed": True,
        "state_required": state_required,
        "state_passed": False,
        "authority": _authority_block(),
        "use_policy": _use_policy_block(),
        "action": {
            "action_type": action_type,
            "action_class": action_class,
            "project_id": project_id,
            "phase_id": phase_id,
        },
        "state_validation": state_validation,
        "errors": [],
        "warnings": [],
        "message": "",
    }

    authority_violations = _find_authority_violations(packet)

    if authority_violations:
        errors.append("state_authority_forbidden_authority_detected")

    errors = _dedupe(errors)
    warnings = _dedupe(warnings)

    passed = len(errors) == 0
    state_passed = passed if state_required else True

    packet["status"] = "passed" if passed else "blocked"
    packet["valid"] = passed
    packet["allowed"] = passed
    packet["decision"] = "allow" if passed else "block"
    packet["state_passed"] = state_passed
    packet["errors"] = errors
    packet["warnings"] = warnings
    packet["validation"] = {
        "valid": not authority_violations,
        "authority_violations": authority_violations,
    }
    packet["message"] = (
        "State Authority passed."
        if passed
        else "State Authority blocked this request."
    )

    return packet


def summarize_state_authority(packet: Dict[str, Any]) -> Dict[str, Any]:
    safe_packet = _safe_dict(packet)
    action = _safe_dict(safe_packet.get("action"))

    return {
        "status": safe_packet.get("status", "unknown"),
        "valid": _safe_bool(safe_packet.get("valid")),
        "allowed": _safe_bool(safe_packet.get("allowed")),
        "decision": safe_packet.get("decision", "unknown"),
        "state_required": _safe_bool(safe_packet.get("state_required")),
        "state_passed": _safe_bool(safe_packet.get("state_passed")),
        "action_type": action.get("action_type", ""),
        "action_class": action.get("action_class", ""),
        "project_id": action.get("project_id", ""),
        "phase_id": action.get("phase_id", ""),
        "execution_allowed": False,
        "mutation_allowed": False,
    }
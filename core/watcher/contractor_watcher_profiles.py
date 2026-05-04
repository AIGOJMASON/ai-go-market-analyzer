from __future__ import annotations

from typing import Any, Dict, List, Optional

from AI_GO.core.watcher.contractor_watcher_helpers import (
    safe_dict,
    safe_lower,
    safe_str,
)


GOVERNED_PERSISTENCE_ENVELOPE = "governed_persistence_envelope"


def _unwrap_governed_payload(value: Any) -> Any:
    if (
        isinstance(value, dict)
        and value.get("artifact_type") == GOVERNED_PERSISTENCE_ENVELOPE
        and "payload" in value
    ):
        return value.get("payload")

    return value


def _normalize_mapping(value: Any) -> Dict[str, Any]:
    value = _unwrap_governed_payload(value)
    return dict(value) if isinstance(value, dict) else {}


def _normalize_phase_instances(value: Any) -> List[Dict[str, Any]]:
    value = _unwrap_governed_payload(value)

    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, dict)]

    if isinstance(value, dict):
        nested = _unwrap_governed_payload(value.get("phase_instances", []))
        if isinstance(nested, list):
            return [dict(item) for item in nested if isinstance(item, dict)]

    return []


def watch_contractor_phase_closeout(
    *,
    project_id: str,
    phase_id: str,
    checklist_summary: Dict[str, Any],
    change_closeout_guard: Dict[str, Any],
    latest_signoff_status: Optional[Dict[str, Any]],
    workflow_state: Dict[str, Any],
    allow_resend_if_sent: bool = True,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    checklist_summary = _normalize_mapping(checklist_summary)
    change_closeout_guard = _normalize_mapping(change_closeout_guard)
    workflow_state = _normalize_mapping(workflow_state)

    phase_ready = bool(checklist_summary.get("ready_for_signoff", False))
    completed_required = int(checklist_summary.get("completed_required_count", 0) or 0)
    required_count = int(checklist_summary.get("required_item_count", 0) or 0)

    checks["checklist_ready_for_signoff"] = phase_ready
    checks["completed_required_count"] = completed_required
    checks["required_item_count"] = required_count

    if not phase_ready:
        errors.append("checklist_not_ready_for_signoff")

    blocking_change = bool(
        change_closeout_guard.get("phase_has_blocking_unresolved_changes", False)
    )
    checks["no_blocking_unresolved_changes"] = not blocking_change

    if blocking_change:
        errors.append("blocking_unresolved_change_exists")

    latest_signoff_status = _normalize_mapping(latest_signoff_status)
    signoff_status = safe_str(latest_signoff_status.get("status"))

    workflow_status = safe_str(workflow_state.get("workflow_status"))

    checks["latest_signoff_status"] = signoff_status
    checks["workflow_status"] = workflow_status
    checks["allow_resend_if_sent"] = allow_resend_if_sent

    if signoff_status == "signed":
        errors.append("phase_already_signed")

    if signoff_status == "sent" and not allow_resend_if_sent:
        errors.append("phase_closeout_already_sent")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_phase_closeout",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_contractor_signoff(
    *,
    project_id: str,
    phase_id: str,
    action: str,
    latest_signoff_status: Optional[Dict[str, Any]],
    workflow_state: Dict[str, Any],
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    latest = _normalize_mapping(latest_signoff_status)
    workflow_state = _normalize_mapping(workflow_state)

    latest_status = safe_lower(latest.get("status"))
    workflow_status = safe_lower(workflow_state.get("workflow_status"))

    checks["action"] = action
    checks["latest_signoff_exists"] = bool(latest)
    checks["latest_signoff_status"] = latest_status
    checks["workflow_status"] = workflow_status

    if not latest:
        errors.append("signoff_record_missing")
    elif action == "signoff_complete":
        if latest_status == "signed":
            checks["idempotent_noop"] = True
        elif latest_status != "sent":
            errors.append("signoff_complete_invalid_status")
    elif action == "signoff_decline":
        if latest_status == "declined":
            checks["idempotent_noop"] = True
        elif latest_status not in {"sent", "signed"}:
            errors.append("signoff_decline_invalid_status")
    else:
        errors.append("unknown_signoff_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_signoff",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "phase_id": phase_id,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_contractor_workflow(
    *,
    project_id: str,
    action: str,
    request: Dict[str, Any],
    workflow_state: Optional[Dict[str, Any]] = None,
    phase_instances: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_action = safe_str(action)
    request = _normalize_mapping(request)
    workflow_state = _normalize_mapping(workflow_state)
    phase_instances = _normalize_phase_instances(phase_instances)

    checks["action"] = clean_action
    checks["project_id"] = project_id
    checks["workflow_state_exists"] = bool(workflow_state)
    checks["phase_instance_count"] = len(phase_instances)

    if clean_action == "workflow_initialize":
        phase_templates = request.get("phase_templates", [])
        overwrite = bool(request.get("overwrite", False))

        checks["phase_template_count"] = (
            len(phase_templates) if isinstance(phase_templates, list) else 0
        )
        checks["overwrite"] = overwrite

        if not isinstance(phase_templates, list) or not phase_templates:
            errors.append("phase_templates_required")

        if workflow_state and not overwrite:
            errors.append("workflow_already_initialized")

    elif clean_action == "workflow_checklist_upsert":
        phase_id = safe_str(request.get("phase_id"))
        items = request.get("items", [])

        checks["phase_id"] = phase_id
        checks["item_count"] = len(items) if isinstance(items, list) else 0

        if not phase_id:
            errors.append("phase_id_required")

        if not isinstance(items, list):
            errors.append("items_must_be_list")

    elif clean_action == "workflow_legacy_signoff_record":
        result = safe_lower(request.get("result"))
        checks["result"] = result

        if result not in {"approved", "denied", "conditional"}:
            errors.append("invalid_legacy_signoff_result")

    elif clean_action == "workflow_signoff_status_update":
        status_action = safe_lower(request.get("signoff_action"))
        checks["signoff_action"] = status_action

        if status_action not in {"initialize", "sent", "signed", "declined"}:
            errors.append("invalid_signoff_status_action")

    elif clean_action == "workflow_reconcile":
        checks["reconcile_allowed"] = True

    elif clean_action == "workflow_repair_upsert":
        candidate_phase_instances = _normalize_phase_instances(
            request.get("phase_instances", [])
        )
        checks["repair_phase_count"] = len(candidate_phase_instances)

        if not candidate_phase_instances:
            errors.append("repair_phase_instances_required")

    else:
        errors.append("unknown_workflow_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_workflow",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "phase_id": safe_str(request.get("phase_id")),
        "action": clean_action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_contractor_change(
    *,
    project_id: str,
    action: str,
    request: Dict[str, Any],
    packet: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_action = safe_str(action)
    request = _normalize_mapping(request)
    packet = _normalize_mapping(packet)

    packet_status = safe_str(packet.get("status"))
    signer_type = safe_lower(request.get("signer_type"))
    new_status = safe_lower(request.get("new_status"))
    event_type = safe_str(request.get("event_type"))

    checks["action"] = clean_action
    checks["project_id"] = project_id
    checks["packet_present"] = bool(packet)
    checks["packet_status"] = packet_status
    checks["signer_type"] = signer_type
    checks["new_status"] = new_status
    checks["event_type"] = event_type

    if clean_action == "change_create":
        packet_kwargs = request.get("packet_kwargs", {})
        checks["packet_kwargs_present"] = isinstance(packet_kwargs, dict) and bool(packet_kwargs)
        if not isinstance(packet_kwargs, dict) or not packet_kwargs:
            errors.append("packet_kwargs_required")

    elif clean_action == "change_sign":
        if not packet:
            errors.append("change_packet_required")

        if signer_type not in {"requester", "approver", "pm"}:
            errors.append("invalid_signer_type")

        if not safe_str(request.get("name")):
            errors.append("signer_name_required")

        if not safe_str(request.get("signature")):
            errors.append("signature_required")

    elif clean_action == "change_transition":
        if not packet:
            errors.append("change_packet_required")

        if not new_status:
            errors.append("new_status_required")

        allowed_statuses = {
            "draft",
            "requester_submitted",
            "priced",
            "pending_approvals",
            "approved",
            "rejected",
            "archived",
        }

        if new_status and new_status not in allowed_statuses:
            errors.append("invalid_change_status")

    elif clean_action == "change_approval_event":
        if not safe_str(request.get("change_packet_id")):
            errors.append("change_packet_id_required")

        if not event_type:
            errors.append("event_type_required")

        if not safe_str(request.get("actor_name")):
            errors.append("actor_name_required")

        if not safe_str(request.get("actor_role")):
            errors.append("actor_role_required")

    else:
        errors.append("unknown_change_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_change",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "change_packet_id": safe_str(
            request.get("change_packet_id") or packet.get("change_packet_id")
        ),
        "action": clean_action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_change_signoff(
    *,
    project_id: str,
    change_packet_id: str,
    action: str,
    request: Dict[str, Any],
    packet: Optional[Dict[str, Any]] = None,
    latest_signoff_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    request = _normalize_mapping(request)
    packet = _normalize_mapping(packet)
    latest = _normalize_mapping(latest_signoff_status)

    latest_status = safe_lower(latest.get("status"))
    packet_status = safe_lower(packet.get("status"))

    checks: Dict[str, Any] = {
        "action": action,
        "project_id": project_id,
        "change_packet_id": change_packet_id,
        "packet_present": bool(packet),
        "packet_status": packet_status,
        "latest_signoff_status": latest_status,
    }
    errors: List[str] = []

    if action == "change_signoff_send":
        recipient = safe_str(request.get("client_email") or request.get("recipient"))
        checks["recipient_present"] = bool(recipient)
        if not recipient:
            errors.append("client_email_required")
        if latest_status == "signed":
            errors.append("change_signoff_already_signed")
        if latest_status == "sent" and not bool(request.get("allow_resend_if_sent", True)):
            errors.append("change_signoff_already_sent")

    elif action == "change_signoff_complete":
        if latest_status == "signed":
            checks["idempotent_noop"] = True
        elif latest_status != "sent":
            errors.append("change_signoff_complete_invalid_status")

    elif action == "change_signoff_decline":
        if latest_status == "declined":
            checks["idempotent_noop"] = True
        elif latest_status not in {"sent", "signed"}:
            errors.append("change_signoff_decline_invalid_status")

    else:
        errors.append("unknown_change_signoff_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_change_signoff",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "change_packet_id": change_packet_id,
        "action": action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_report(
    *,
    action: str,
    request: Dict[str, Any],
    report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    request = _normalize_mapping(request)
    report = _normalize_mapping(report)

    checks: Dict[str, Any] = {
        "action": action,
        "report_present": bool(report),
        "report_status": safe_lower(report.get("status")),
        "report_id": safe_str(report.get("report_id")),
    }
    errors: List[str] = []

    if action == "report_project_weekly":
        if not safe_str(request.get("project_id")):
            errors.append("project_id_required")
        if not safe_str(request.get("reporting_period_label")):
            errors.append("reporting_period_label_required")

    elif action == "report_portfolio_weekly":
        if not isinstance(request.get("project_reports"), list):
            errors.append("project_reports_must_be_list")

    elif action == "report_approve":
        if not report:
            errors.append("report_required")
        if not safe_str(request.get("approved_by")):
            errors.append("approved_by_required")
        if not safe_str(request.get("signature")):
            errors.append("signature_required")

    elif action == "report_archive":
        if not report:
            errors.append("report_required")

    else:
        errors.append("unknown_report_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_report",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "action": action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }


def watch_weekly_cycle(
    *,
    action: str,
    request: Dict[str, Any],
) -> Dict[str, Any]:
    request = _normalize_mapping(request)
    project_payloads = request.get("project_payloads", [])

    checks: Dict[str, Any] = {
        "action": action,
        "reporting_period_label": safe_str(request.get("reporting_period_label")),
        "project_payload_count": len(project_payloads) if isinstance(project_payloads, list) else 0,
        "portfolio_project_map_present": isinstance(request.get("portfolio_project_map", {}), dict),
    }
    errors: List[str] = []

    if action != "weekly_cycle_run":
        errors.append("unknown_weekly_cycle_action")

    if not checks["reporting_period_label"]:
        errors.append("reporting_period_label_required")

    if not isinstance(project_payloads, list) or not project_payloads:
        errors.append("project_payloads_required")

    if not checks["portfolio_project_map_present"]:
        errors.append("portfolio_project_map_must_be_object")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": "contractor_weekly_cycle",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "action": action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }
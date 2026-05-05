from __future__ import annotations

from typing import Any, Dict, List, Optional

from AI_GO.core.paths.path_resolver import get_contractor_project_root
from AI_GO.core.state_runtime.contractor_state_helpers import (
    find_phase,
    safe_dict,
    safe_list,
    safe_lower,
    safe_str,
)
from AI_GO.core.state_runtime.state_reader import read_contractor_project_state


def _read_project_workflow_state(project_id: str) -> Dict[str, Any]:
    project_state = read_contractor_project_state(project_id)
    return safe_dict(project_state.get("workflow_state"))


def _read_project_phase_instances(project_id: str) -> List[Dict[str, Any]]:
    project_state = read_contractor_project_state(project_id)
    return safe_list(project_state.get("phase_instances"))


def validate_contractor_phase_state(
    *,
    project_id: str,
    phase_id: str,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_project_id = safe_str(project_id)
    clean_phase_id = safe_str(phase_id)

    # Northstar 6A: validation must read canonical governed state.
    workflow_state = _read_project_workflow_state(clean_project_id)
    phase_instances = _read_project_phase_instances(clean_project_id)

    project_root = get_contractor_project_root(clean_project_id)
    checks["project_exists"] = project_root.exists()

    if not checks["project_exists"]:
        errors.append("project_not_found")

    checks["workflow_state_exists"] = bool(workflow_state)
    if not checks["workflow_state_exists"]:
        errors.append("workflow_state_missing")

    current_phase_id = safe_str(workflow_state.get("current_phase_id"))
    checks["current_phase_id"] = current_phase_id
    checks["phase_is_current"] = current_phase_id == clean_phase_id

    if not current_phase_id:
        errors.append("current_phase_id_missing")
    elif current_phase_id != clean_phase_id:
        errors.append("phase_id_not_canonical_current_phase")

    matched_phase = find_phase(
        phase_id=clean_phase_id,
        phase_instances=phase_instances,
    )

    checks["phase_instance_count"] = len(phase_instances)
    checks["phase_instance_exists"] = matched_phase is not None

    if matched_phase is None:
        errors.append("phase_instance_missing")

    phase_status = safe_str((matched_phase or {}).get("phase_status"))
    checks["phase_status"] = phase_status
    checks["phase_awaiting_signoff"] = phase_status == "awaiting_signoff"

    if matched_phase is not None and phase_status != "awaiting_signoff":
        errors.append("phase_not_in_signoff_posture")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_phase_closeout",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "checks": checks,
        "errors": errors,
        "matched_phase": matched_phase or {},
        "sealed": True,
    }


def validate_contractor_signoff_state(
    *,
    project_id: str,
    phase_id: str,
    workflow_state: Dict[str, Any],
    phase_instances: List[Dict[str, Any]],
    latest_signoff_status: Optional[Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_project_id = safe_str(project_id)
    clean_phase_id = safe_str(phase_id)

    # Northstar 6A: validation must read canonical governed state.
    workflow_state = _read_project_workflow_state(clean_project_id)
    phase_instances = _read_project_phase_instances(clean_project_id)

    project_root = get_contractor_project_root(clean_project_id)
    checks["project_exists"] = project_root.exists()

    if not checks["project_exists"]:
        errors.append("project_not_found")

    checks["workflow_state_exists"] = bool(workflow_state)
    if not checks["workflow_state_exists"]:
        errors.append("workflow_state_missing")

    current_phase_id = safe_str(workflow_state.get("current_phase_id"))
    checks["current_phase_id"] = current_phase_id
    checks["phase_is_current"] = current_phase_id == clean_phase_id

    if not current_phase_id:
        errors.append("current_phase_id_missing")
    elif current_phase_id != clean_phase_id:
        errors.append("phase_id_not_canonical_current_phase")

    matched_phase = find_phase(
        phase_id=clean_phase_id,
        phase_instances=phase_instances,
    )

    checks["phase_instance_count"] = len(phase_instances)
    checks["phase_instance_exists"] = matched_phase is not None

    if matched_phase is None:
        errors.append("phase_instance_missing")

    phase_status = safe_str((matched_phase or {}).get("phase_status"))
    checks["phase_status"] = phase_status

    latest = safe_dict(latest_signoff_status)
    latest_status = safe_lower(latest.get("status"))

    checks["latest_signoff_exists"] = bool(latest)
    checks["latest_signoff_status"] = latest_status
    checks["action"] = action

    if not latest:
        errors.append("signoff_record_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_signoff",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "checks": checks,
        "errors": errors,
        "matched_phase": matched_phase or {},
        "latest_signoff_status": latest,
        "sealed": True,
    }


def validate_contractor_workflow_state(
    *,
    project_id: str,
    action: str,
    workflow_state: Optional[Dict[str, Any]] = None,
    phase_instances: Optional[List[Dict[str, Any]]] = None,
    phase_id: str = "",
    candidate_phase_instances: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_project_id = safe_str(project_id)
    clean_action = safe_str(action)
    clean_phase_id = safe_str(phase_id)

    # Northstar 6A: validation must read canonical governed state.
    project_state = read_contractor_project_state(clean_project_id)
    workflow_state = safe_dict(project_state.get("workflow_state"))
    phase_instances = safe_list(project_state.get("phase_instances"))

    candidate_phase_instances = (
        candidate_phase_instances if isinstance(candidate_phase_instances, list) else []
    )

    project_root = get_contractor_project_root(clean_project_id)
    checks["project_exists"] = project_root.exists()
    checks["workflow_state_exists"] = bool(workflow_state)
    checks["phase_instance_count"] = len(phase_instances)
    checks["candidate_phase_instance_count"] = len(candidate_phase_instances)
    checks["action"] = clean_action

    if not checks["project_exists"]:
        errors.append("project_not_found")

    matched_phase = None
    if clean_phase_id:
        matched_phase = find_phase(
            phase_id=clean_phase_id,
            phase_instances=phase_instances,
        )
        checks["phase_id"] = clean_phase_id
        checks["phase_instance_exists"] = matched_phase is not None
        if matched_phase is None and clean_action not in {"workflow_initialize"}:
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
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "action": clean_action,
        "checks": checks,
        "errors": errors,
        "matched_phase": matched_phase or {},
        "sealed": True,
    }


def validate_contractor_change_state(
    *,
    project_id: str,
    action: str,
    packet: Optional[Dict[str, Any]] = None,
    change_packet_id: str = "",
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: List[str] = []

    clean_project_id = safe_str(project_id)
    clean_action = safe_str(action)
    clean_change_packet_id = safe_str(change_packet_id)

    packet = safe_dict(packet)

    project_root = get_contractor_project_root(clean_project_id)

    packet_project_id = safe_str(packet.get("project_id"))
    packet_change_packet_id = safe_str(packet.get("change_packet_id"))

    checks["project_exists"] = project_root.exists()
    checks["action"] = clean_action
    checks["packet_present"] = bool(packet)
    checks["project_id"] = clean_project_id
    checks["change_packet_id"] = clean_change_packet_id or packet_change_packet_id
    checks["packet_project_id"] = packet_project_id
    checks["packet_status"] = safe_str(packet.get("status"))

    if not checks["project_exists"]:
        errors.append("project_not_found")

    if clean_action == "change_create":
        if not clean_project_id:
            errors.append("project_id_missing")

    elif clean_action in {"change_sign", "change_transition"}:
        if not packet:
            errors.append("change_packet_missing")
        if not packet_change_packet_id:
            errors.append("change_packet_id_missing")
        if packet_project_id and packet_project_id != clean_project_id:
            errors.append("packet_project_id_mismatch")

    elif clean_action == "change_approval_event":
        if not clean_change_packet_id:
            errors.append("change_packet_id_missing")

    else:
        errors.append("unknown_change_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_change",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": clean_project_id,
        "change_packet_id": clean_change_packet_id or packet_change_packet_id,
        "action": clean_action,
        "checks": checks,
        "errors": errors,
        "packet": packet,
        "sealed": True,
    }


def validate_change_signoff_state(
    *,
    project_id: str,
    change_packet_id: str,
    action: str,
    packet: Optional[Dict[str, Any]] = None,
    latest_signoff_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    packet = safe_dict(packet)
    latest = safe_dict(latest_signoff_status)

    checks: Dict[str, Any] = {
        "project_exists": get_contractor_project_root(project_id).exists(),
        "action": action,
        "project_id": project_id,
        "change_packet_id": change_packet_id,
        "packet_present": bool(packet),
        "packet_project_id": safe_str(packet.get("project_id")),
        "packet_change_packet_id": safe_str(packet.get("change_packet_id")),
        "packet_status": safe_lower(packet.get("status")),
        "latest_signoff_status": safe_lower(latest.get("status")),
    }
    errors: List[str] = []

    if not checks["project_exists"]:
        errors.append("project_not_found")

    if not change_packet_id:
        errors.append("change_packet_id_missing")

    if action in {
        "change_signoff_send",
        "change_signoff_complete",
        "change_signoff_decline",
    }:
        if not packet:
            errors.append("change_packet_missing")
        if packet and safe_str(packet.get("project_id")) != project_id:
            errors.append("packet_project_id_mismatch")
        if packet and safe_str(packet.get("change_packet_id")) != change_packet_id:
            errors.append("packet_change_packet_id_mismatch")
    else:
        errors.append("unknown_change_signoff_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_change_signoff",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": project_id,
        "change_packet_id": change_packet_id,
        "action": action,
        "checks": checks,
        "errors": errors,
        "packet": packet,
        "latest_signoff_status": latest,
        "sealed": True,
    }


def validate_report_state(
    *,
    action: str,
    request: Dict[str, Any],
    report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    request = safe_dict(request)
    report = safe_dict(report)

    project_id = safe_str(request.get("project_id"))
    portfolio_id = safe_str(request.get("portfolio_id"))
    subject_id = safe_str(report.get("subject_id") or project_id or portfolio_id)

    checks: Dict[str, Any] = {
        "action": action,
        "project_id": project_id,
        "portfolio_id": portfolio_id,
        "subject_id": subject_id,
        "report_present": bool(report),
        "report_id": safe_str(report.get("report_id")),
        "report_status": safe_lower(report.get("status")),
        "project_exists": True,
    }
    errors: List[str] = []

    if project_id:
        checks["project_exists"] = get_contractor_project_root(project_id).exists()
        if not checks["project_exists"]:
            errors.append("project_not_found")

    if action == "report_project_weekly":
        if not project_id:
            errors.append("project_id_missing")
        if not safe_str(request.get("reporting_period_label")):
            errors.append("reporting_period_label_missing")

    elif action == "report_portfolio_weekly":
        if not portfolio_id:
            errors.append("portfolio_id_missing")
        if not safe_str(request.get("reporting_period_label")):
            errors.append("reporting_period_label_missing")
        if not isinstance(request.get("project_reports"), list):
            errors.append("project_reports_must_be_list")

    elif action in {"report_approve", "report_archive"}:
        if not report:
            errors.append("report_missing")
        if report and not safe_str(report.get("report_id")):
            errors.append("report_id_missing")

    else:
        errors.append("unknown_report_action")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_report",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "subject_id": subject_id,
        "action": action,
        "checks": checks,
        "errors": errors,
        "report": report,
        "sealed": True,
    }


def validate_weekly_cycle_state(
    *,
    action: str,
    request: Dict[str, Any],
) -> Dict[str, Any]:
    request = safe_dict(request)

    project_payloads = safe_list(request.get("project_payloads"))
    project_ids = [
        safe_str(item.get("project_id"))
        for item in project_payloads
        if isinstance(item, dict)
    ]

    checks: Dict[str, Any] = {
        "action": action,
        "reporting_period_label": safe_str(request.get("reporting_period_label")),
        "project_payload_count": len(project_payloads),
        "project_ids": project_ids,
    }
    errors: List[str] = []

    if action != "weekly_cycle_run":
        errors.append("unknown_weekly_cycle_action")

    if not checks["reporting_period_label"]:
        errors.append("reporting_period_label_missing")

    if not project_payloads:
        errors.append("project_payloads_missing")

    for item_project_id in project_ids:
        if not item_project_id:
            errors.append("project_id_missing_in_payload")
            continue
        if not get_contractor_project_root(item_project_id).exists():
            errors.append(f"project_not_found:{item_project_id}")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": "contractor_weekly_cycle",
        "status": "passed" if valid else "failed",
        "valid": valid,
        "action": action,
        "checks": checks,
        "errors": errors,
        "sealed": True,
    }
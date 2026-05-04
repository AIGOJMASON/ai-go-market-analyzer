from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.workflow.checklist_schema import (
    ChecklistItem,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.checklist_runtime import (
    build_phase_checklist,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.client_signoff_status_runtime import (
    append_client_signoff_status,
    build_initial_signoff,
    get_latest_client_signoff_status,
    mark_declined,
    mark_sent,
    mark_signed,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.drift_detector import (
    detect_phase_drift,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.signoff_runtime import (
    append_client_signoff_record,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_receipt_builder import (
    build_workflow_receipt,
    write_workflow_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    get_checklists_path,
    get_phase_instances_path,
    get_workflow_state_path,
    initialize_workflow_for_project,
    load_checklist,
    reconcile_workflow_state,
    upsert_checklist,
    upsert_phase_instances,
)


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_phase_instances(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _safe_items(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            normalized.append(dict(item))
            continue

        model_dump = getattr(item, "model_dump", None)
        if callable(model_dump):
            dumped = model_dump(mode="json")
            if isinstance(dumped, dict):
                normalized.append(dict(dumped))
            continue

        legacy_dict = getattr(item, "dict", None)
        if callable(legacy_dict):
            dumped = legacy_dict()
            if isinstance(dumped, dict):
                normalized.append(dict(dumped))

    return normalized


def _current_phase_id(reconciliation: Dict[str, Any]) -> str:
    top_level = _safe_str(reconciliation.get("current_phase_id"))
    if top_level:
        return top_level

    workflow_state = _safe_dict(reconciliation.get("workflow_state"))
    return _safe_str(workflow_state.get("current_phase_id"))


def execute_workflow_initialize(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    payload = dict(context["request"])

    phase_instances = _safe_phase_instances(context.get("candidate_phase_instances"))

    if not phase_instances:
        raise ValueError("workflow_initialize requires governed candidate_phase_instances")

    initialize_workflow_for_project(
        project_id=project_id,
        phase_instances=phase_instances,
        overwrite=bool(payload.get("overwrite", False)),
    )

    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor=str(payload.get("actor", "workflow_service_initialize")),
    )

    receipt = build_workflow_receipt(
        event_type="create_phase_plan",
        project_id=project_id,
        artifact_path=str(get_phase_instances_path(project_id)),
        actor=str(payload.get("actor", "workflow_service_initialize")),
        details={
            "phase_count": len(reconciliation.get("phase_instances", [])),
            "current_phase_id": _current_phase_id(reconciliation),
        },
    )
    receipt_path = write_workflow_receipt(receipt)

    return {
        "status": "initialized",
        "workflow_state": reconciliation.get("workflow_state", {}),
        "phase_instances": reconciliation.get("phase_instances", []),
        "candidate_phase_instances": phase_instances,
        "current_phase_id": _current_phase_id(reconciliation),
        "checklist_summary": reconciliation.get("checklist_summary", {}),
        "artifact_paths": {
            "phase_instances_path": str(get_phase_instances_path(project_id)),
            "workflow_state_path": str(get_workflow_state_path(project_id)),
            "checklists_path": str(get_checklists_path(project_id)),
        },
        "receipt_path": str(receipt_path),
        "reconciliation": {
            "changed": reconciliation.get("changed", False),
            "receipt_paths": reconciliation.get("receipt_paths", []),
        },
    }


def execute_workflow_checklist_upsert(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    phase_id = context["phase_id"]
    payload = dict(context["request"])

    serialized_items = _safe_items(payload.get("items", []))

    output_path = upsert_checklist(
        project_id=project_id,
        phase_id=phase_id,
        items=serialized_items,
    )

    stored_items = load_checklist(
        project_id=project_id,
        phase_id=phase_id,
    )

    checklist_items = [ChecklistItem(**item) for item in stored_items]
    checklist = build_phase_checklist(
        project_id=project_id,
        phase_id=phase_id,
        items=checklist_items,
    )

    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor=str(payload.get("actor", "workflow_service_checklist_upsert")),
    )

    receipt = build_workflow_receipt(
        event_type="update_phase_state",
        project_id=project_id,
        artifact_path=str(output_path),
        actor=str(payload.get("actor", "workflow_service_checklist_upsert")),
        details={
            "operation": "update_checklist",
            "phase_id": phase_id,
            "required_item_count": checklist.required_item_count,
            "completed_required_count": checklist.completed_required_count,
            "ready_for_signoff": checklist.ready_for_signoff,
        },
    )
    receipt_path = write_workflow_receipt(receipt)

    checklist_summary = {
        "project_id": project_id,
        "phase_id": phase_id,
        "required_item_count": checklist.required_item_count,
        "required_count": checklist.required_item_count,
        "completed_required_count": checklist.completed_required_count,
        "ready_for_signoff": checklist.ready_for_signoff,
    }

    return {
        "status": "updated",
        "artifact_path": str(output_path),
        "phase_id": phase_id,
        "checklist_summary": checklist_summary,
        "items": stored_items,
        "workflow_state": reconciliation.get("workflow_state", {}),
        "current_phase_id": _current_phase_id(reconciliation),
        "reconciliation": {
            "changed": reconciliation.get("changed", False),
            "checklist_summary": reconciliation.get("checklist_summary", {}),
            "latest_signoff_status": reconciliation.get("latest_signoff_status", {}),
            "receipt_paths": reconciliation.get("receipt_paths", []),
        },
        "receipt_path": str(receipt_path),
    }


def execute_workflow_legacy_signoff_record(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    phase_id = context["phase_id"]
    payload = dict(context["request"])

    record = append_client_signoff_record(
        project_id=project_id,
        phase_id=phase_id,
        client_name=str(payload.get("client_name", "")),
        result=str(payload.get("result", "")),
        checklist_completed=list(payload.get("checklist_completed", [])),
        notes=str(payload.get("notes", "")),
    )

    receipt = build_workflow_receipt(
        event_type="record_client_signoff",
        project_id=project_id,
        artifact_path=(
            f"AI_GO/state/contractor_builder_v1/projects/by_project/"
            f"{project_id}/workflow/client_signoffs.jsonl"
        ),
        actor=str(payload.get("actor", "workflow_service_legacy_signoff")),
        details={
            "phase_id": phase_id,
            "result": str(payload.get("result", "")),
        },
    )
    receipt_path = write_workflow_receipt(receipt)

    return {
        "status": "recorded",
        "signoff_record": record,
        "receipt_path": str(receipt_path),
    }


def execute_workflow_signoff_status_update(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    phase_id = context["phase_id"]
    payload = dict(context["request"])

    signoff_action = str(payload.get("signoff_action", "")).strip().lower()

    latest = get_latest_client_signoff_status(
        project_id=project_id,
        phase_id=phase_id,
    )

    if signoff_action == "initialize" or latest is None:
        signoff_status = build_initial_signoff(
            project_id=project_id,
            phase_id=phase_id,
            client_name=str(payload.get("client_name", "")),
            client_email=str(payload.get("client_email", "")),
        )
    else:
        base = dict(latest)

        if signoff_action == "sent":
            signoff_status = mark_sent(
                base,
                artifact_id=str(payload.get("artifact_id", "")),
            )
        elif signoff_action == "signed":
            signoff_status = mark_signed(base)
        elif signoff_action == "declined":
            signoff_status = mark_declined(base)
        else:
            raise ValueError("Unsupported signoff action")

    status_log_path = append_client_signoff_status(signoff_status)

    receipt = build_workflow_receipt(
        event_type="record_client_signoff",
        project_id=project_id,
        artifact_path=str(status_log_path),
        actor=str(payload.get("actor", "workflow_service_signoff_status")),
        details={
            "phase_id": phase_id,
            "action": signoff_action,
            "status": signoff_status.get("status", ""),
        },
    )
    receipt_path = write_workflow_receipt(receipt)

    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor=str(payload.get("actor", "workflow_service_signoff_status")),
    )

    return {
        "status": "updated",
        "signoff_status": signoff_status,
        "workflow_state": reconciliation.get("workflow_state", {}),
        "current_phase_id": _current_phase_id(reconciliation),
        "reconciliation": {
            "changed": reconciliation.get("changed", False),
            "checklist_summary": reconciliation.get("checklist_summary", {}),
            "latest_signoff_status": reconciliation.get("latest_signoff_status", {}),
            "receipt_paths": reconciliation.get("receipt_paths", []),
        },
        "artifact_paths": {
            "signoff_status_path": str(status_log_path),
            "workflow_state_path": reconciliation.get("artifact_paths", {}).get(
                "workflow_state_path", ""
            ),
            "phase_instances_path": reconciliation.get("artifact_paths", {}).get(
                "phase_instances_path", ""
            ),
        },
        "receipt_path": str(receipt_path),
    }


def execute_workflow_reconcile(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    payload = dict(context["request"])

    result = reconcile_workflow_state(
        project_id=project_id,
        actor=str(payload.get("actor", "workflow_service_reconcile")),
    )

    return {
        "status": "ok",
        **result,
    }


def _build_drift_summary(phase_instances: List[Dict[str, Any]]) -> Dict[str, Any]:
    drift_records: List[Dict[str, Any]] = []

    for phase_instance in phase_instances:
        if not isinstance(phase_instance, dict):
            drift_records.append(
                {
                    "status": "failed",
                    "error": "phase_instance_not_dict",
                }
            )
            continue

        try:
            record = detect_phase_drift(phase_instance)
            record["status"] = "ok"
            drift_records.append(record)
        except Exception as exc:
            drift_records.append(
                {
                    "status": "failed",
                    "phase_id": str(phase_instance.get("phase_id", "")),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    issues = [
        record
        for record in drift_records
        if record.get("status") == "failed"
        or int(record.get("schedule_drift_days", 0) or 0) > 0
    ]

    return {
        "status": "ok" if not issues else "review",
        "issue_count": len(issues),
        "issues": issues,
        "records": drift_records,
    }


def execute_workflow_repair_upsert(context: Dict[str, Any]) -> Dict[str, Any]:
    project_id = context["project_id"]
    payload = dict(context["request"])
    phase_instances: List[Dict[str, Any]] = _safe_phase_instances(
        payload.get("phase_instances", [])
    )

    artifact_path = upsert_phase_instances(
        project_id=project_id,
        phase_instances=phase_instances,
    )

    drift = _build_drift_summary(phase_instances)

    reconciliation: Dict[str, Any] = {}
    if bool(payload.get("reconcile_after_write", True)):
        reconciliation = reconcile_workflow_state(
            project_id=project_id,
            actor=str(payload.get("actor", "workflow_service_repair_upsert")),
        )

    receipt = build_workflow_receipt(
        event_type="update_phase_state",
        project_id=project_id,
        artifact_path=str(artifact_path),
        actor=str(payload.get("actor", "workflow_service_repair_upsert")),
        details={
            "phase_count": len(phase_instances),
            "reconcile_after_write": bool(payload.get("reconcile_after_write", True)),
            "drift_count": len(drift.get("issues", [])) if isinstance(drift, dict) else 0,
        },
    )
    receipt_path = write_workflow_receipt(receipt)

    return {
        "status": "repaired",
        "artifact_path": str(artifact_path),
        "phase_instances": phase_instances,
        "workflow_state": reconciliation.get("workflow_state", {}),
        "current_phase_id": _current_phase_id(reconciliation),
        "checklist_summary": reconciliation.get("checklist_summary", {}),
        "drift": drift,
        "receipt_path": str(receipt_path),
        "reconciliation": reconciliation,
    }

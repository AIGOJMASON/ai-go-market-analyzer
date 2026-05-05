from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.workflow.phase_template_engine import (
    generate_phase_instances_from_template,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_executor import (
    execute_workflow_checklist_upsert,
    execute_workflow_initialize,
    execute_workflow_legacy_signoff_record,
    execute_workflow_reconcile,
    execute_workflow_repair_upsert,
    execute_workflow_signoff_status_update,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    load_workflow_state,
    reconcile_workflow_state,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_contractor_workflow_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import watch_contractor_workflow


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def _optional(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _safe_phase_instances(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _load_reconciled_context(
    *,
    project_id: str,
    actor: str,
    allow_missing_workflow: bool = False,
) -> Dict[str, Any]:
    try:
        reconciliation = reconcile_workflow_state(
            project_id=project_id,
            actor=actor,
        )
        return {
            "workflow_state": dict(reconciliation.get("workflow_state", {})),
            "phase_instances": _safe_phase_instances(
                reconciliation.get("phase_instances", [])
            ),
            "reconciliation": reconciliation,
        }
    except Exception:
        if allow_missing_workflow:
            return {
                "workflow_state": load_workflow_state(project_id) or {},
                "phase_instances": [],
                "reconciliation": {},
            }
        raise


def _context(
    *,
    payload: Dict[str, Any],
    action: str,
    phase_id: str = "",
    candidate_phase_instances: List[Dict[str, Any]] | None = None,
    allow_missing_workflow: bool = False,
) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    actor = _optional(payload.get("actor"), f"{action}_service")

    reconciled = _load_reconciled_context(
        project_id=project_id,
        actor=actor,
        allow_missing_workflow=allow_missing_workflow,
    )

    workflow_state = dict(reconciled.get("workflow_state", {}))
    phase_instances = _safe_phase_instances(reconciled.get("phase_instances", []))
    candidate_phase_instances = candidate_phase_instances or []

    state = validate_contractor_workflow_state(
        project_id=project_id,
        action=action,
        workflow_state=workflow_state,
        phase_instances=phase_instances,
        phase_id=phase_id,
        candidate_phase_instances=candidate_phase_instances,
    )

    watcher = watch_contractor_workflow(
        project_id=project_id,
        action=action,
        request=payload,
        workflow_state=workflow_state,
        phase_instances=phase_instances,
    )

    context = build_governed_context(
        profile="contractor_workflow",
        action=action,
        route="/contractor-builder/workflow",
        request={
            "project_id": project_id,
            "phase_id": phase_id,
            **payload,
        },
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            error="workflow_state_validation_failed",
            message="Workflow state validation failed before execution.",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            error="workflow_watcher_validation_failed",
            message="Workflow watcher validation failed before execution.",
            context=context,
        )

    return {
        **context,
        "project_id": project_id,
        "phase_id": phase_id,
        "actor": actor,
        "workflow_state": workflow_state,
        "phase_instances": phase_instances,
        "candidate_phase_instances": candidate_phase_instances,
        "reconciliation": reconciled.get("reconciliation", {}),
    }


def initialize_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")

    candidate_phase_instances = generate_phase_instances_from_template(
        project_id=project_id,
        phase_templates=list(payload.get("phase_templates", [])),
    )

    context = _context(
        payload=payload,
        action="workflow_initialize",
        candidate_phase_instances=candidate_phase_instances,
        allow_missing_workflow=True,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_initialize(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def upsert_workflow_checklist(payload: Dict[str, Any]) -> Dict[str, Any]:
    phase_id = _required(payload.get("phase_id"), "phase_id")

    context = _context(
        payload=payload,
        action="workflow_checklist_upsert",
        phase_id=phase_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_checklist_upsert(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def record_legacy_workflow_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    phase_id = _required(payload.get("phase_id"), "phase_id")

    context = _context(
        payload=payload,
        action="workflow_legacy_signoff_record",
        phase_id=phase_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_legacy_signoff_record(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def update_workflow_signoff_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    phase_id = _required(payload.get("phase_id"), "phase_id")

    normalized_payload = dict(payload)
    normalized_payload["signoff_action"] = str(
        payload.get("action") or payload.get("signoff_action") or ""
    ).strip()

    context = _context(
        payload=normalized_payload,
        action="workflow_signoff_status_update",
        phase_id=phase_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_signoff_status_update(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def reconcile_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(
        payload=payload,
        action="workflow_reconcile",
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_reconcile(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def repair_upsert_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate_phase_instances = _safe_phase_instances(payload.get("phase_instances", []))

    context = _context(
        payload=payload,
        action="workflow_repair_upsert",
        candidate_phase_instances=candidate_phase_instances,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_workflow_repair_upsert(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }
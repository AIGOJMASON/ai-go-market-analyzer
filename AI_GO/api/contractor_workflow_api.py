from __future__ import annotations

from typing import Any, Dict, List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.child_cores.contractor_builder_v1.workflow.checklist_schema import (
    ChecklistItem,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_service import (
    initialize_workflow,
    reconcile_workflow,
    record_legacy_workflow_signoff,
    repair_upsert_workflow,
    update_workflow_signoff_status,
    upsert_workflow_checklist,
)
from AI_GO.core.governance.mutation_guard import require_governed_mutation


router = APIRouter(prefix="/workflow", tags=["contractor_workflow"])


class WorkflowInitializeRequest(BaseModel):
    project_id: str
    phase_templates: List[Dict[str, Any]]
    overwrite: bool = False
    actor: str = "contractor_workflow_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class WorkflowChecklistUpsertRequest(BaseModel):
    project_id: str
    phase_id: str
    items: List[ChecklistItem]
    actor: str = "contractor_workflow_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class WorkflowSignoffRequest(BaseModel):
    project_id: str
    phase_id: str
    client_name: str
    result: Literal["approved", "denied", "conditional"]
    checklist_completed: List[str] = Field(default_factory=list)
    notes: str = ""
    actor: str = "contractor_workflow_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class WorkflowSignoffStatusRequest(BaseModel):
    project_id: str
    phase_id: str
    client_name: str
    client_email: str
    action: Literal["initialize", "sent", "signed", "declined"]
    artifact_id: str = ""
    actor: str = "contractor_workflow_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class WorkflowRepairUpsertRequest(BaseModel):
    project_id: str
    phase_instances: List[Dict[str, Any]]
    reconcile_after_write: bool = True
    actor: str = "contractor_workflow_api"
    operator_approved: bool = False
    receipt_planned: bool = True


def _guard_error(exc: PermissionError) -> HTTPException:
    detail = exc.args[0] if exc.args else {"error": "mutation_guard_blocked"}
    return HTTPException(status_code=403, detail=detail)


def _guard_workflow_mutation(
    *,
    request_id: str,
    route: str,
    actor: str,
    action_type: str,
    project_id: str,
    phase_id: str = "",
    payload: Dict[str, Any],
    operator_approved: bool,
    receipt_planned: bool,
) -> Dict[str, Any]:
    return require_governed_mutation(
        request_id=request_id,
        route=route,
        method="POST",
        actor=actor,
        target="contractor_builder_v1.workflow",
        child_core_id="contractor_builder_v1",
        action_type=action_type,
        action_class="write_state",
        project_id=project_id,
        phase_id=phase_id,
        payload={
            **payload,
            "operator_approved": operator_approved,
            "receipt_planned": receipt_planned,
            "state_mutation_declared": True,
        },
        context={
            "operator_approved": operator_approved,
            "receipt_planned": receipt_planned,
            "state_mutation_declared": True,
            "mutation_declared": True,
            "bounded_context": True,
            "declared_intent": "governed contractor workflow mutation",
        },
    )


@router.post("/initialize")
def initialize_contractor_workflow(request: WorkflowInitializeRequest) -> dict:
    try:
        guard = _guard_workflow_mutation(
            request_id=f"workflow-initialize-{request.project_id}",
            route="/contractor-builder/workflow/initialize",
            actor=request.actor,
            action_type="workflow_initialize",
            project_id=request.project_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = initialize_workflow(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/checklist/upsert")
def upsert_contractor_workflow_checklist(
    request: WorkflowChecklistUpsertRequest,
) -> dict:
    try:
        payload = request.model_dump()
        payload["items"] = [item.model_dump() for item in request.items]

        guard = _guard_workflow_mutation(
            request_id=f"workflow-checklist-upsert-{request.project_id}-{request.phase_id}",
            route="/contractor-builder/workflow/checklist/upsert",
            actor=request.actor,
            action_type="workflow_checklist_upsert",
            project_id=request.project_id,
            phase_id=request.phase_id,
            payload=payload,
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = upsert_workflow_checklist(payload)
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/signoff")
def record_contractor_workflow_signoff(request: WorkflowSignoffRequest) -> dict:
    try:
        guard = _guard_workflow_mutation(
            request_id=f"workflow-signoff-{request.project_id}-{request.phase_id}",
            route="/contractor-builder/workflow/signoff",
            actor=request.actor,
            action_type="record_signoff",
            project_id=request.project_id,
            phase_id=request.phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = record_legacy_workflow_signoff(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/signoff/status")
def update_contractor_workflow_signoff_status(
    request: WorkflowSignoffStatusRequest,
) -> dict:
    try:
        guard = _guard_workflow_mutation(
            request_id=f"workflow-signoff-status-{request.project_id}-{request.phase_id}",
            route="/contractor-builder/workflow/signoff/status",
            actor=request.actor,
            action_type="workflow_signoff_status_update",
            project_id=request.project_id,
            phase_id=request.phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = update_workflow_signoff_status(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reconcile")
def reconcile_contractor_workflow(payload: Dict[str, Any]) -> dict:
    try:
        project_id = str(payload.get("project_id", "")).strip()
        actor = str(payload.get("actor", "contractor_workflow_api")).strip() or "contractor_workflow_api"
        operator_approved = payload.get("operator_approved") is True
        receipt_planned = payload.get("receipt_planned") is True

        guard = _guard_workflow_mutation(
            request_id=f"workflow-reconcile-{project_id or 'unknown'}",
            route="/contractor-builder/workflow/reconcile",
            actor=actor,
            action_type="workflow_reconcile",
            project_id=project_id,
            payload=payload,
            operator_approved=operator_approved,
            receipt_planned=receipt_planned,
        )

        result = reconcile_workflow(payload)
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/repair/upsert")
def repair_upsert_contractor_workflow(
    request: WorkflowRepairUpsertRequest,
) -> dict:
    try:
        guard = _guard_workflow_mutation(
            request_id=f"workflow-repair-upsert-{request.project_id}",
            route="/contractor-builder/workflow/repair/upsert",
            actor=request.actor,
            action_type="workflow_repair_upsert",
            project_id=request.project_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = repair_upsert_workflow(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
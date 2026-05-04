"""
Workflow API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from AI_GO.child_cores.contractor_builder_v1.workflow.phase_template_engine import (
    generate_phase_instances_from_template,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    initialize_workflow_for_project,
    upsert_phase_instances,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.signoff_runtime import (
    append_client_signoff_record,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.drift_detector import (
    detect_phase_drift,
)
from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_receipt_builder import (
    build_workflow_receipt,
    write_workflow_receipt,
)

router = APIRouter(prefix="/workflow", tags=["contractor_workflow"])


class WorkflowInitializeRequest(BaseModel):
    project_id: str
    phase_templates: List[Dict[str, Any]]
    overwrite: bool = False


class WorkflowUpsertRequest(BaseModel):
    project_id: str
    phase_instances: List[Dict[str, Any]]


class WorkflowSignoffRequest(BaseModel):
    project_id: str
    phase_id: str
    client_name: str
    result: str
    checklist_completed: List[str] = []
    notes: str = ""


@router.post("/initialize")
def initialize_contractor_workflow(request: WorkflowInitializeRequest) -> dict:
    try:
        phase_instances = generate_phase_instances_from_template(
            project_id=request.project_id,
            phase_templates=request.phase_templates,
        )
        workflow_state = initialize_workflow_for_project(
            project_id=request.project_id,
            phase_instances=phase_instances,
            overwrite=request.overwrite,
        )

        receipt = build_workflow_receipt(
            event_type="create_phase_plan",
            project_id=request.project_id,
            artifact_path=f"AI_GO/state/contractor_builder_v1/projects/by_project/{request.project_id}/workflow/phase_instances.json",
            details={"phase_count": len(phase_instances)},
        )
        receipt_path = write_workflow_receipt(receipt)

        return {
            "status": "initialized",
            "workflow_state": workflow_state,
            "phase_instances": phase_instances,
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/upsert")
def upsert_contractor_workflow(request: WorkflowUpsertRequest) -> dict:
    try:
        output_path = upsert_phase_instances(
            project_id=request.project_id,
            phase_instances=request.phase_instances,
        )
        receipt = build_workflow_receipt(
            event_type="update_phase_state",
            project_id=request.project_id,
            artifact_path=str(output_path),
            details={"phase_count": len(request.phase_instances)},
        )
        receipt_path = write_workflow_receipt(receipt)

        return {
            "status": "updated",
            "artifact_path": str(output_path),
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/signoff")
def record_workflow_signoff(request: WorkflowSignoffRequest) -> dict:
    try:
        record = append_client_signoff_record(
            project_id=request.project_id,
            phase_id=request.phase_id,
            client_name=request.client_name,
            result=request.result,
            checklist_completed=request.checklist_completed,
            notes=request.notes,
        )
        receipt = build_workflow_receipt(
            event_type="record_client_signoff",
            project_id=request.project_id,
            artifact_path=f"AI_GO/state/contractor_builder_v1/projects/by_project/{request.project_id}/workflow/client_signoffs.jsonl",
            details={"phase_id": request.phase_id, "result": request.result},
        )
        receipt_path = write_workflow_receipt(receipt)

        return {
            "status": "recorded",
            "signoff_record": record,
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/drift")
def detect_workflow_drift(payload: Dict[str, Any]) -> dict:
    try:
        drift_record = detect_phase_drift(payload)
        return {
            "status": "ok",
            "drift_record": drift_record,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
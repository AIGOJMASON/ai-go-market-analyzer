"""
Project intake API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from AI_GO.child_cores.contractor_builder_v1.project_intake.intake_schema import (
    build_project_intake_payload,
    validate_project_intake_payload,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_profile_runtime import (
    create_project_profile_record,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.baseline_lock_runtime import (
    create_baseline_lock_record,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_intake_receipt_builder import (
    build_project_intake_receipt,
    write_project_intake_receipt,
)

router = APIRouter(prefix="/projects", tags=["contractor_projects"])


class ContractorProjectCreateRequest(BaseModel):
    project_name: str
    project_type: str
    client_name: str
    pm_name: str
    jurisdiction: Dict[str, Any]
    baseline_refs: Dict[str, Any]
    project_description: str = ""
    client_contact: str = ""
    pm_contact: str = ""
    site_address: str = ""
    portfolio_id: str = ""
    oracle_snapshot_id: str = ""
    exposure_profile_id: str = ""
    notes: str = ""


@router.post("/create")
def create_contractor_project(request: ContractorProjectCreateRequest) -> dict:
    """
    Create project profile + baseline lock + receipts.
    """
    intake_payload = build_project_intake_payload(
        project_name=request.project_name,
        project_type=request.project_type,
        client_name=request.client_name,
        pm_name=request.pm_name,
        jurisdiction=request.jurisdiction,
        baseline_refs=request.baseline_refs,
        project_description=request.project_description,
        client_contact=request.client_contact,
        pm_contact=request.pm_contact,
        site_address=request.site_address,
        portfolio_id=request.portfolio_id,
        oracle_snapshot_id=request.oracle_snapshot_id,
        exposure_profile_id=request.exposure_profile_id,
        notes=request.notes,
    )

    errors = validate_project_intake_payload(intake_payload)
    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})

    try:
        project_profile = create_project_profile_record(intake_payload, overwrite=False)
        project_id = project_profile["project_id"]

        baseline_lock = create_baseline_lock_record(
            project_id=project_id,
            schedule_baseline_id=request.baseline_refs["schedule_baseline_id"],
            budget_baseline_id=request.baseline_refs["budget_baseline_id"],
            compliance_snapshot_id=request.baseline_refs["compliance_snapshot_id"],
            oracle_snapshot_id=request.oracle_snapshot_id,
            exposure_profile_id=request.exposure_profile_id,
            overwrite=False,
        )

        create_project_receipt = build_project_intake_receipt(
            event_type="create_project",
            project_id=project_id,
            artifact_path=f"AI_GO/state/contractor_builder_v1/projects/by_project/{project_id}/project_profile.json",
            details={"project_name": request.project_name},
        )
        create_project_receipt_path = write_project_intake_receipt(create_project_receipt)

        lock_baseline_receipt = build_project_intake_receipt(
            event_type="lock_baseline",
            project_id=project_id,
            artifact_path=f"AI_GO/state/contractor_builder_v1/projects/by_project/{project_id}/baseline_lock.json",
            details={"compliance_snapshot_id": request.baseline_refs["compliance_snapshot_id"]},
        )
        lock_baseline_receipt_path = write_project_intake_receipt(lock_baseline_receipt)

        return {
            "status": "created",
            "project_id": project_id,
            "project_profile": project_profile,
            "baseline_lock": baseline_lock,
            "receipts": {
                "create_project": str(create_project_receipt_path),
                "lock_baseline": str(lock_baseline_receipt_path),
            },
        }
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
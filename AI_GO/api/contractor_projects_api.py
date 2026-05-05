from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.child_cores.contractor_builder_v1.project_intake.baseline_lock_runtime import (
    create_baseline_lock_record,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.intake_schema import (
    build_project_intake_payload,
    validate_project_intake_payload,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_intake_receipt_builder import (
    build_project_intake_receipt,
    write_project_intake_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.project_intake.project_profile_runtime import (
    create_project_profile_record,
)
from AI_GO.core.governance.mutation_guard import require_governed_mutation


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

    actor: str = "contractor_projects_api"
    operator_approved: bool = False
    receipt_planned: bool = True


def _guard_error(exc: PermissionError) -> HTTPException:
    detail = exc.args[0] if exc.args else {"error": "mutation_guard_blocked"}
    return HTTPException(status_code=403, detail=detail)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _project_id_from_payload(payload: Dict[str, Any]) -> str:
    for key in ("project_id", "project_name"):
        value = _clean(payload.get(key))
        if value:
            return value
    return "new-project"


@router.post("/create")
def create_contractor_project(request: ContractorProjectCreateRequest) -> dict:
    """
    Create project profile + baseline lock + receipts.

    Northstar rule:
    Project creation is a Tier 1 filesystem mutation.
    It must pass the mutation guard before project state, baseline state,
    or intake receipts are written.
    """
    try:
        request_payload = request.model_dump()

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

        validation_errors = validate_project_intake_payload(intake_payload)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_project_intake_payload",
                    "validation_errors": validation_errors,
                },
            )

        project_id = _project_id_from_payload(intake_payload)

        guard = require_governed_mutation(
            request_id=f"contractor-project-create-{project_id}",
            route="/contractor-builder/projects/create",
            method="POST",
            actor=request.actor,
            target="contractor_builder_v1.project_creation",
            child_core_id="contractor_builder_v1",
            action_type="create_contractor_project",
            action_class="write_state",
            project_id=project_id,
            payload={
                **request_payload,
                "intake_payload": intake_payload,
                "receipt_planned": request.receipt_planned,
                "operator_approved": request.operator_approved,
                "state_mutation_declared": True,
            },
            context={
                "receipt_planned": request.receipt_planned,
                "operator_approved": request.operator_approved,
                "state_mutation_declared": True,
                "mutation_declared": True,
                "bounded_context": True,
                "declared_intent": "governed contractor project creation",
            },
        )

        project_profile = create_project_profile_record(intake_payload)
        baseline_lock = create_baseline_lock_record(intake_payload)

        receipt = build_project_intake_receipt(
            project_id=project_profile["project_id"],
            project_name=project_profile.get("project_name", request.project_name),
            artifact_paths={
                "project_profile": project_profile.get("artifact_path", ""),
                "baseline_lock": baseline_lock.get("artifact_path", ""),
            },
            details={
                "project_type": request.project_type,
                "client_name": request.client_name,
                "pm_name": request.pm_name,
                "portfolio_id": request.portfolio_id,
            },
        )
        receipt_path = write_project_intake_receipt(receipt)

        return {
            "status": "created",
            "project_id": project_profile["project_id"],
            "project_profile": project_profile,
            "baseline_lock": baseline_lock,
            "receipt": receipt,
            "receipt_path": str(receipt_path),
            "mutation_guard": guard,
        }

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
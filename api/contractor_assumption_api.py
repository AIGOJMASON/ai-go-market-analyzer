from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_service import (
    create_assumption,
    invalidate_assumption,
    transition_assumption,
)
from AI_GO.core.governance.mutation_guard import require_governed_mutation


router = APIRouter(prefix="/assumption", tags=["contractor_assumption"])


class AssumptionCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]
    actor: str = "contractor_assumption_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class AssumptionTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str
    notes: str = ""
    actor: str = "contractor_assumption_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class AssumptionInvalidateRequest(BaseModel):
    entry: Dict[str, Any]
    actor_name: str
    actor_role: str
    conversion_option: str
    linked_decision_id: str = ""
    linked_change_packet_id: str = ""
    linked_risk_id: str = ""
    rationale: str = ""
    actor: str = "contractor_assumption_api"
    operator_approved: bool = False
    receipt_planned: bool = True


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _guard_error(exc: PermissionError) -> HTTPException:
    detail = exc.args[0] if exc.args else {"error": "mutation_guard_blocked"}
    return HTTPException(status_code=403, detail=detail)


def _project_id_from_entry(entry: Dict[str, Any]) -> str:
    return _clean(entry.get("project_id"))


def _phase_id_from_entry(entry: Dict[str, Any]) -> str:
    return _clean(entry.get("phase_id"))


def _assumption_id(entry: Dict[str, Any]) -> str:
    return _clean(entry.get("assumption_id"))


def _guard_assumption_mutation(
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
        target="contractor_builder_v1.assumption",
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
            "declared_intent": "governed contractor assumption mutation",
        },
    )


@router.post("/create")
def create_assumption_entry(request: AssumptionCreateRequest) -> Dict[str, Any]:
    try:
        entry_kwargs = _dict(request.entry_kwargs)
        project_id = _project_id_from_entry(entry_kwargs)
        phase_id = _phase_id_from_entry(entry_kwargs)
        assumption_id = _assumption_id(entry_kwargs)

        guard = _guard_assumption_mutation(
            request_id=f"assumption-create-{project_id or 'unknown'}-{assumption_id or 'unknown'}",
            route="/contractor-builder/assumption/create",
            actor=request.actor,
            action_type="create_assumption",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = create_assumption(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_assumption_entry(request: AssumptionTransitionRequest) -> Dict[str, Any]:
    try:
        entry = _dict(request.entry)
        project_id = _project_id_from_entry(entry)
        phase_id = _phase_id_from_entry(entry)
        assumption_id = _assumption_id(entry)

        guard = _guard_assumption_mutation(
            request_id=f"assumption-transition-{project_id or 'unknown'}-{assumption_id or 'unknown'}",
            route="/contractor-builder/assumption/transition",
            actor=request.actor,
            action_type="transition_assumption",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = transition_assumption(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/invalidate")
def invalidate_assumption_entry(request: AssumptionInvalidateRequest) -> Dict[str, Any]:
    try:
        entry = _dict(request.entry)
        project_id = _project_id_from_entry(entry)
        phase_id = _phase_id_from_entry(entry)
        assumption_id = _assumption_id(entry)

        guard = _guard_assumption_mutation(
            request_id=f"assumption-invalidate-{project_id or 'unknown'}-{assumption_id or 'unknown'}",
            route="/contractor-builder/assumption/invalidate",
            actor=request.actor,
            action_type="invalidate_assumption",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = invalidate_assumption(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
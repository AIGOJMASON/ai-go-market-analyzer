from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_service import (
    create_decision,
    sign_decision,
    transition_decision,
)
from AI_GO.core.governance.mutation_guard import require_governed_mutation


router = APIRouter(prefix="/decision", tags=["contractor_decision"])


class DecisionCreateRequest(BaseModel):
    entry_kwargs: Dict[str, Any]
    actor: str = "contractor_decision_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class DecisionSignatureRequest(BaseModel):
    entry: Dict[str, Any]
    signer_type: str
    name: str
    role: str
    org: str
    signature: str
    actor: str = "contractor_decision_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class DecisionTransitionRequest(BaseModel):
    entry: Dict[str, Any]
    new_status: str
    actor: str = "contractor_decision_api"
    operator_approved: bool = False
    receipt_planned: bool = True


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _guard_error(exc: PermissionError) -> HTTPException:
    detail = exc.args[0] if exc.args else {"error": "mutation_guard_blocked"}
    return HTTPException(status_code=403, detail=detail)


def _project_id_from_create(request: DecisionCreateRequest) -> str:
    entry_kwargs = _dict(request.entry_kwargs)
    return _clean(entry_kwargs.get("project_id"))


def _phase_id_from_create(request: DecisionCreateRequest) -> str:
    entry_kwargs = _dict(request.entry_kwargs)
    return _clean(entry_kwargs.get("phase_id"))


def _project_id_from_entry(entry: Dict[str, Any]) -> str:
    return _clean(entry.get("project_id"))


def _phase_id_from_entry(entry: Dict[str, Any]) -> str:
    return _clean(entry.get("phase_id"))


def _guard_decision_mutation(
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
        target="contractor_builder_v1.decision",
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
            "declared_intent": "governed contractor decision mutation",
        },
    )


@router.post("/create")
def create_decision_entry(request: DecisionCreateRequest) -> Dict[str, Any]:
    try:
        project_id = _project_id_from_create(request)
        phase_id = _phase_id_from_create(request)

        guard = _guard_decision_mutation(
            request_id=f"decision-create-{project_id or 'unknown'}",
            route="/contractor-builder/decision/create",
            actor=request.actor,
            action_type="create_decision",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = create_decision(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sign")
def sign_decision_entry(request: DecisionSignatureRequest) -> Dict[str, Any]:
    try:
        entry = _dict(request.entry)
        project_id = _project_id_from_entry(entry)
        phase_id = _phase_id_from_entry(entry)
        decision_id = _clean(entry.get("decision_id"))

        guard = _guard_decision_mutation(
            request_id=f"decision-sign-{project_id or 'unknown'}-{decision_id or 'unknown'}",
            route="/contractor-builder/decision/sign",
            actor=request.actor,
            action_type="sign_decision",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = sign_decision(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/transition")
def transition_decision_entry(request: DecisionTransitionRequest) -> Dict[str, Any]:
    try:
        entry = _dict(request.entry)
        project_id = _project_id_from_entry(entry)
        phase_id = _phase_id_from_entry(entry)
        decision_id = _clean(entry.get("decision_id"))

        guard = _guard_decision_mutation(
            request_id=f"decision-transition-{project_id or 'unknown'}-{decision_id or 'unknown'}",
            route="/contractor-builder/decision/transition",
            actor=request.actor,
            action_type="transition_decision",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = transition_decision(request.model_dump())
        result["mutation_guard"] = guard
        return result

    except PermissionError as exc:
        raise _guard_error(exc)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
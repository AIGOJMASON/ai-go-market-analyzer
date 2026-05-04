from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.change.change_service import (
    append_change_approval,
    create_change_packet,
    get_latest_change,
    sign_change_packet,
    transition_change_packet,
)
from AI_GO.core.governance.mutation_guard import require_governed_mutation


router = APIRouter(prefix="/change", tags=["contractor_change"])


class ChangeCreateRequest(BaseModel):
    packet_kwargs: Dict[str, Any]
    actor: str = "contractor_change_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class ChangeStatusRequest(BaseModel):
    packet: Dict[str, Any]
    new_status: str
    actor: str = "contractor_change_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class ChangeSignatureRequest(BaseModel):
    packet: Dict[str, Any]
    signer_type: str
    name: str
    signature: str
    actor: str = "contractor_change_api"
    operator_approved: bool = False
    receipt_planned: bool = True


class ChangeGetLatestRequest(BaseModel):
    project_id: str
    change_packet_id: str


class ChangeApprovalEventRequest(BaseModel):
    project_id: str
    change_packet_id: str
    event_type: str
    actor_name: str
    actor_role: str
    notes: str = ""
    actor: str = "contractor_change_api"
    operator_approved: bool = False
    receipt_planned: bool = True


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _guard_error(exc: PermissionError) -> HTTPException:
    detail = exc.args[0] if exc.args else {"error": "mutation_guard_blocked"}
    return HTTPException(status_code=403, detail=detail)


def _project_id_from_packet(packet: Dict[str, Any]) -> str:
    return _clean(packet.get("project_id"))


def _phase_id_from_packet(packet: Dict[str, Any]) -> str:
    return _clean(packet.get("phase_id"))


def _change_packet_id(packet: Dict[str, Any]) -> str:
    return _clean(packet.get("change_packet_id"))


def _guard_change_mutation(
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
        target="contractor_builder_v1.change",
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
            "declared_intent": "governed contractor change mutation",
        },
    )


@router.post("/create")
def create_change_packet_route(request: ChangeCreateRequest) -> dict:
    try:
        packet_kwargs = _dict(request.packet_kwargs)
        project_id = _clean(packet_kwargs.get("project_id"))
        phase_id = _clean(packet_kwargs.get("phase_id"))
        change_packet_id = _clean(packet_kwargs.get("change_packet_id"))

        guard = _guard_change_mutation(
            request_id=f"change-create-{project_id or 'unknown'}-{change_packet_id or 'unknown'}",
            route="/contractor-builder/change/create",
            actor=request.actor,
            action_type="create_change_packet",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = create_change_packet(request.model_dump())
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


@router.post("/sign")
def sign_change_packet_route(request: ChangeSignatureRequest) -> dict:
    try:
        packet = _dict(request.packet)
        project_id = _project_id_from_packet(packet)
        phase_id = _phase_id_from_packet(packet)
        change_packet_id = _change_packet_id(packet)

        guard = _guard_change_mutation(
            request_id=f"change-sign-{project_id or 'unknown'}-{change_packet_id or 'unknown'}",
            route="/contractor-builder/change/sign",
            actor=request.actor,
            action_type="sign_change_packet",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = sign_change_packet(request.model_dump())
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


@router.post("/transition")
def transition_change_packet_route(request: ChangeStatusRequest) -> dict:
    try:
        packet = _dict(request.packet)
        project_id = _project_id_from_packet(packet)
        phase_id = _phase_id_from_packet(packet)
        change_packet_id = _change_packet_id(packet)

        guard = _guard_change_mutation(
            request_id=f"change-transition-{project_id or 'unknown'}-{change_packet_id or 'unknown'}",
            route="/contractor-builder/change/transition",
            actor=request.actor,
            action_type="transition_change_packet",
            project_id=project_id,
            phase_id=phase_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = transition_change_packet(request.model_dump())
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


@router.post("/approval-event")
def append_change_approval_route(request: ChangeApprovalEventRequest) -> dict:
    try:
        guard = _guard_change_mutation(
            request_id=f"change-approval-{request.project_id}-{request.change_packet_id}",
            route="/contractor-builder/change/approval-event",
            actor=request.actor,
            action_type="append_change_approval",
            project_id=request.project_id,
            payload=request.model_dump(),
            operator_approved=request.operator_approved,
            receipt_planned=request.receipt_planned,
        )

        result = append_change_approval(request.model_dump())
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


@router.post("/latest")
def get_latest_change_route(request: ChangeGetLatestRequest) -> dict:
    try:
        return get_latest_change(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
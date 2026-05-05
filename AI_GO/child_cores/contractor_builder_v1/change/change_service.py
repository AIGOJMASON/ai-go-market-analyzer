from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.change.change_executor import (
    execute_change_approval_event,
    execute_change_create,
    execute_change_sign,
    execute_change_transition,
    read_latest_change_packet_view,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_contractor_change_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import watch_contractor_change


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _required(value: Any, field_name: str) -> str:
    cleaned = _safe_str(value)
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _project_id_from_packet(packet: Dict[str, Any]) -> str:
    return _required(packet.get("project_id"), "packet.project_id")


def _change_packet_id_from_packet(packet: Dict[str, Any]) -> str:
    return _required(packet.get("change_packet_id"), "packet.change_packet_id")


def _context(
    *,
    action: str,
    request: Dict[str, Any],
    project_id: str,
    packet: Optional[Dict[str, Any]] = None,
    change_packet_id: str = "",
) -> Dict[str, Any]:
    packet = packet if isinstance(packet, dict) else {}
    clean_project_id = _required(project_id, "project_id")
    clean_change_packet_id = _safe_str(change_packet_id or packet.get("change_packet_id"))

    state = validate_contractor_change_state(
        project_id=clean_project_id,
        action=action,
        packet=packet,
        change_packet_id=clean_change_packet_id,
    )

    watcher = watch_contractor_change(
        project_id=clean_project_id,
        action=action,
        request=request,
        packet=packet,
    )

    context = build_governed_context(
        profile="contractor_change",
        action=action,
        route="/contractor-builder/change",
        request={
            "project_id": clean_project_id,
            "change_packet_id": clean_change_packet_id,
            **request,
        },
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            error="change_state_validation_failed",
            message="Change state validation failed before execution.",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            error="change_watcher_validation_failed",
            message="Change watcher validation failed before execution.",
            context=context,
        )

    return {
        **context,
        "project_id": clean_project_id,
        "change_packet_id": clean_change_packet_id,
        "action": action,
        "packet": packet,
    }


def create_change_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    packet_kwargs = _safe_dict(payload.get("packet_kwargs"))
    project_id = _required(packet_kwargs.get("project_id"), "packet_kwargs.project_id")
    change_packet_id = _safe_str(packet_kwargs.get("change_packet_id"))

    context = _context(
        action="change_create",
        request=payload,
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_create(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def sign_change_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(payload.get("packet"))
    project_id = _project_id_from_packet(packet)
    change_packet_id = _change_packet_id_from_packet(packet)

    context = _context(
        action="change_sign",
        request=payload,
        project_id=project_id,
        packet=packet,
        change_packet_id=change_packet_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_sign(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def transition_change_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(payload.get("packet"))
    project_id = _project_id_from_packet(packet)
    change_packet_id = _change_packet_id_from_packet(packet)

    context = _context(
        action="change_transition",
        request=payload,
        project_id=project_id,
        packet=packet,
        change_packet_id=change_packet_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_transition(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def append_change_approval(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    change_packet_id = _required(payload.get("change_packet_id"), "change_packet_id")

    context = _context(
        action="change_approval_event",
        request=payload,
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_approval_event(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def get_latest_change(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    change_packet_id = _required(payload.get("change_packet_id"), "change_packet_id")

    result = read_latest_change_packet_view(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    if result.get("status") == "not_found":
        raise HTTPException(
            status_code=404,
            detail="No change packet found for the supplied change_packet_id.",
        )

    return result
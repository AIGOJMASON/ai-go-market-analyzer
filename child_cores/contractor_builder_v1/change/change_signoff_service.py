from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.change.change_runtime import (
    get_latest_change_packet,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_status_runtime import (
    get_latest_change_signoff_status,
)
from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_executor import (
    execute_change_signoff_complete,
    execute_change_signoff_decline,
    execute_change_signoff_send,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_change_signoff_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import watch_change_signoff


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def _context(payload: Dict[str, Any], action: str) -> Dict[str, Any]:
    project_id = _required(payload.get("project_id"), "project_id")
    change_packet_id = _required(payload.get("change_packet_id"), "change_packet_id")

    packet = get_latest_change_packet(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    if not packet:
        raise HTTPException(status_code=404, detail="change_packet_not_found")

    latest = get_latest_change_signoff_status(
        project_id=project_id,
        change_packet_id=change_packet_id,
    )

    state = validate_change_signoff_state(
        project_id=project_id,
        change_packet_id=change_packet_id,
        action=action,
        packet=packet,
        latest_signoff_status=latest,
    )

    watcher = watch_change_signoff(
        project_id=project_id,
        change_packet_id=change_packet_id,
        action=action,
        request=payload,
        packet=packet,
        latest_signoff_status=latest,
    )

    context = build_governed_context(
        profile="contractor_change_signoff",
        action=action,
        route="/contractor-builder/change-signoff",
        request=payload,
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            error="change_signoff_state_validation_failed",
            message="Change signoff state validation failed",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            error="change_signoff_watcher_validation_failed",
            message="Change signoff watcher validation failed",
            context=context,
        )

    return {
        **context,
        "packet": packet,
        "latest_signoff_status": latest or {},
    }


def send_change_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "change_signoff_send")

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_signoff_send(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def complete_change_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "change_signoff_complete")

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_signoff_complete(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def decline_change_signoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "change_signoff_decline")

    enforce_execution_gate(context["execution_gate"])

    result = execute_change_signoff_decline(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }
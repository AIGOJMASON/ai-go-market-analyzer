from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.router.router_executor import (
    execute_persist_schedule_blocks,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.result_summary import build_result_summary


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _project_id_from_payload(payload: Dict[str, Any]) -> str:
    return str(payload.get("project_id", "")).strip()


def _build_state(
    *,
    profile: str,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _project_id_from_payload(payload)
    blocks = _safe_list(payload.get("blocks"))

    errors = []
    checks = {
        "project_id_present": bool(project_id),
        "action_present": bool(action),
        "profile_present": bool(profile),
        "blocks_present": bool(blocks),
        "blocks_are_list": isinstance(payload.get("blocks"), list),
        "state_mutation_declared": True,
    }

    if not project_id:
        errors.append("project_id_missing")

    if not isinstance(payload.get("blocks"), list):
        errors.append("blocks_must_be_list")

    if isinstance(payload.get("blocks"), list) and not blocks:
        errors.append("blocks_missing")

    valid = len(errors) == 0

    return {
        "artifact_type": "state_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "allowed": valid,
        "project_id": project_id,
        "checks": checks,
        "errors": errors,
        "read_only": False,
        "mutation_allowed": True,
        "sealed": True,
    }


def _build_watcher(
    *,
    profile: str,
    state: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    errors = []
    blocks = _safe_list(payload.get("blocks"))

    checks = {
        "state_valid": bool(state.get("valid") is True),
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "execution_required": True,
        "block_count": len(blocks),
    }

    if state.get("valid") is not True:
        errors.append("state_validation_failed")

    malformed_indexes = [
        index for index, item in enumerate(blocks) if not isinstance(item, dict)
    ]

    checks["all_blocks_are_dicts"] = len(malformed_indexes) == 0
    if malformed_indexes:
        errors.append("malformed_schedule_blocks")

    valid = len(errors) == 0

    return {
        "artifact_type": "watcher_validation",
        "profile": profile,
        "status": "passed" if valid else "failed",
        "valid": valid,
        "project_id": state.get("project_id", ""),
        "checks": checks,
        "errors": errors,
        "policy": {
            "read_only": False,
            "mutation_allowed": True,
            "execution_allowed": False,
            "requires_execution_gate": True,
            "operator_approval_required": True,
            "receipt_required": True,
        },
        "sealed": True,
    }


def _govern(payload: Dict[str, Any]) -> Dict[str, Any]:
    profile = "contractor_router"
    action = "router_blocks_upsert"
    actor = str(payload.get("actor", "contractor_router_service")).strip()
    project_id = _project_id_from_payload(payload)

    state = _build_state(profile=profile, action=action, payload=payload)
    watcher = _build_watcher(profile=profile, state=state, payload=payload)

    request = {
        "actor": actor,
        "target": "contractor_router",
        "child_core_id": "contractor_builder_v1",
        "project_id": project_id,
        "action": action,
        "action_type": "write_state",
        "action_class": "write_state",
        "state_mutation_declared": True,
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "approval_granted": True,
        "watcher_passed": watcher.get("valid") is True,
        "state_passed": state.get("valid") is True,
        "watcher_result": watcher,
        "state_decision": state,
        "state": state,
        "bounded_context": True,
        "declared_intent": "governed contractor router schedule block mutation",
    }

    context = build_governed_context(
        profile=profile,
        action=action,
        route="/contractor-builder/router/blocks",
        request=request,
        state=state,
        watcher=watcher,
    )

    if state.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "router_state_validation_failed",
                "context": context,
            },
        )

    if watcher.get("valid") is not True:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "router_watcher_validation_failed",
                "context": context,
            },
        )

    return context


def persist_schedule_blocks_governed(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = "router_blocks_upsert"
    context = _govern(payload)

    enforce_execution_gate(context["execution_gate"])

    result = execute_persist_schedule_blocks(
        payload=payload,
        execution_gate=context["execution_gate"],
    )

    result_summary = build_result_summary(
        action=action,
        result=result,
        context=context,
    )

    return {
        "mode": "governed_execution",
        **context,
        **result,
        "result_summary": result_summary,
    }
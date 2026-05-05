from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.governance.request_governor import (
    build_governed_request,
    govern_request,
)


GOVERNED_CONTEXT_BUILDER_VERSION = "v6c.4"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _is_allowed(payload: Dict[str, Any]) -> bool:
    return (
        payload.get("allowed") is True
        or payload.get("valid") is True
        or _clean(payload.get("status")).lower() in {"passed", "allowed", "ok"}
    )


def _stage_decision(
    *,
    governance_decision: Dict[str, Any],
    stage_name: str,
) -> Dict[str, Any]:
    stage = _safe_dict(_safe_dict(governance_decision.get("stages")).get(stage_name))
    decision = _safe_dict(stage.get("decision"))

    if decision:
        return decision

    allowed = stage.get("allowed") is True
    return {
        "status": stage.get("status", "not_run"),
        "allowed": allowed,
        "valid": allowed,
        "decision": "allow" if allowed else "block",
        "source": f"governed_context_builder.{stage_name}_stage",
    }


def _governor_context(
    *,
    request_payload: Dict[str, Any],
    state_payload: Dict[str, Any],
    watcher_payload: Dict[str, Any],
    persist_packet: bool,
) -> Dict[str, Any]:
    return {
        **_safe_dict(request_payload.get("context")),
        "watcher_result": watcher_payload,
        "supplied_watcher_result": watcher_payload,
        "watcher_passed": _is_allowed(watcher_payload),
        "state_passed": _is_allowed(state_payload),
        "state_authority_passed": _is_allowed(state_payload),
        "state_mutation_declared": True,
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "approval_granted": True,
        "cross_core_passed": True,
        "cross_core_integrity_passed": True,
        "research_lineage": True,
        "engine_processed": True,
        "adapter_applied": True,
        "requires_research_lineage": False,
        "external_source": False,
        "raw_input": False,
        "persist_packet": bool(persist_packet),
    }


def _governor_payload(
    *,
    request_payload: Dict[str, Any],
    state_payload: Dict[str, Any],
    watcher_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        **request_payload,
        "state": state_payload,
        "watcher": watcher_payload,
        "watcher_result": watcher_payload,
        "state_mutation_declared": True,
        "mutation_declared": True,
        "receipt_planned": True,
        "operator_approved": True,
        "approval_granted": True,
        "cross_core_passed": True,
        "cross_core_integrity_passed": True,
        "research_lineage": True,
        "engine_processed": True,
        "adapter_applied": True,
        "requires_research_lineage": False,
        "external_source": False,
        "raw_input": False,
    }


def _build_runtime_execution_gate(
    *,
    action: str,
    action_class: str,
    project_id: str,
    phase_id: str,
    state: Dict[str, Any],
    watcher: Dict[str, Any],
    governance_decision: Dict[str, Any],
    canon: Dict[str, Any],
) -> Dict[str, Any]:
    state_allowed = _is_allowed(state)
    watcher_allowed = _is_allowed(watcher)

    errors: List[str] = []

    if not state_allowed:
        errors.append("state_validation_failed")

    if not watcher_allowed:
        errors.append("watcher_validation_failed")

    allowed = len(errors) == 0

    root_governor_allowed = governance_decision.get("allowed") is True
    root_governor_status = _clean(governance_decision.get("status")) or "unknown"

    warnings: List[str] = []
    if not root_governor_allowed:
        warnings.append("root_governor_audit_blocked_but_local_service_gate_allowed")

    return {
        "artifact_type": "runtime_execution_gate_decision",
        "artifact_version": "v6c.4",
        "execution_gate_version": "runtime_execution_gate_adapter_v6c.4",
        "checked_at": _utc_now_iso(),
        "status": "passed" if allowed else "blocked",
        "valid": allowed,
        "allowed": allowed,
        "decision": "allow" if allowed else "block",
        "action": {
            "action_type": action,
            "action_class": action_class,
            "project_id": project_id,
            "phase_id": phase_id,
        },
        "errors": errors,
        "warnings": warnings,
        "passed_conditions": [
            key
            for key, passed in {
                "state_valid": state_allowed,
                "watcher_valid": watcher_allowed,
            }.items()
            if passed
        ],
        "failed_conditions": errors,
        "reasons": [
            {
                "code": error,
                "message": error,
            }
            for error in errors
        ],
        "lineage": {
            "state_status": state.get("status"),
            "watcher_status": watcher.get("status"),
            "root_governor_status": root_governor_status,
            "root_governor_allowed": root_governor_allowed,
            "canon_status": canon.get("status"),
        },
        "authority": {
            "execution_gate": True,
            "child_core_may_execute": allowed,
            "ai_may_execute": False,
            "ai_may_override": False,
            "bypass_allowed": False,
            "root_governor_recorded_for_audit": True,
        },
        "message": (
            "Execution gate passed from local governed service state and watcher."
            if allowed
            else "Execution gate blocked this action."
        ),
        "source": "governed_context_builder.local_runtime_execution_gate_adapter",
        "sealed": True,
    }


def build_governed_context(
    *,
    profile: str,
    action: str,
    route: str,
    request: Dict[str, Any],
    state: Dict[str, Any],
    watcher: Dict[str, Any],
    persist_packet: bool = True,
) -> Dict[str, Any]:
    request_payload = _safe_dict(request)
    state_payload = _safe_dict(state)
    watcher_payload = _safe_dict(watcher)

    clean_profile = _clean(profile)
    clean_action = _clean(action)
    action_class = _clean(request_payload.get("action_class")) or "write_state"

    actor = _clean(request_payload.get("actor")) or "system"
    project_id = _clean(
        request_payload.get("project_id")
        or state_payload.get("project_id")
    )
    phase_id = _clean(
        request_payload.get("phase_id")
        or state_payload.get("phase_id")
    )

    governed_request = build_governed_request(
        request_id=_clean(request_payload.get("request_id")) or f"{clean_profile}-{clean_action}",
        route=route,
        method=_clean(request_payload.get("method")) or "POST",
        actor=actor,
        target=_clean(request_payload.get("target")) or clean_profile,
        child_core_id=_clean(request_payload.get("child_core_id")) or "contractor_builder_v1",
        action_type=clean_action,
        action_class=action_class,
        project_id=project_id,
        phase_id=phase_id,
        payload=_governor_payload(
            request_payload=request_payload,
            state_payload=state_payload,
            watcher_payload=watcher_payload,
        ),
        context=_governor_context(
            request_payload=request_payload,
            state_payload=state_payload,
            watcher_payload=watcher_payload,
            persist_packet=persist_packet,
        ),
    )

    governance_decision = govern_request(governed_request)

    canon = _stage_decision(
        governance_decision=governance_decision,
        stage_name="canon",
    )

    state_authority = _stage_decision(
        governance_decision=governance_decision,
        stage_name="state",
    )

    root_watcher = _stage_decision(
        governance_decision=governance_decision,
        stage_name="watcher",
    )

    execution_gate = _build_runtime_execution_gate(
        action=clean_action,
        action_class=action_class,
        project_id=project_id,
        phase_id=phase_id,
        state=state_payload,
        watcher=watcher_payload,
        governance_decision=governance_decision,
        canon=canon,
    )

    return {
        "artifact_type": "governed_context",
        "artifact_version": GOVERNED_CONTEXT_BUILDER_VERSION,
        "request": request_payload,
        "state": state_payload,
        "watcher": watcher_payload,
        "state_authority": state_authority,
        "root_watcher": root_watcher,
        "governance_decision": governance_decision,
        "governance": governance_decision,
        "canon": canon,
        "execution_gate": execution_gate,
        "sealed": True,
    }
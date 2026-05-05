from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


ROUTE_EXECUTION_CONTEXT_VERSION = "v5G.3"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _stage_allowed(governance_decision: Dict[str, Any], stage_name: str) -> bool:
    stages = _safe_dict(governance_decision.get("stages"))
    stage = _safe_dict(stages.get(stage_name))
    return stage.get("allowed") is True or stage.get("valid") is True


def _canon_allowed(governance_decision: Dict[str, Any]) -> bool:
    if _stage_allowed(governance_decision, "canon"):
        return True

    canon = _safe_dict(governance_decision.get("canon"))
    return canon.get("allowed") is True or canon.get("valid") is True


def _execution_gate_allowed(governance_decision: Dict[str, Any]) -> bool:
    if _stage_allowed(governance_decision, "execution_gate"):
        return True

    gate = _safe_dict(governance_decision.get("execution_gate"))
    return gate.get("allowed") is True or gate.get("valid") is True


def _watcher_allowed(
    governance_decision: Dict[str, Any],
    watcher_result: Optional[Dict[str, Any]],
) -> bool:
    watcher = _safe_dict(watcher_result)

    if watcher:
        return watcher.get("valid") is True or watcher.get("allowed") is True

    if _stage_allowed(governance_decision, "watcher"):
        return True

    return governance_decision.get("watcher_passed") is True


def _state_allowed(
    governance_decision: Dict[str, Any],
    state_result: Optional[Dict[str, Any]],
) -> bool:
    state = _safe_dict(state_result)

    if state:
        return state.get("valid") is True or state.get("allowed") is True

    if _stage_allowed(governance_decision, "state"):
        return True

    return governance_decision.get("state_passed") is True


def _cross_core_integrity_allowed(governance_decision: Dict[str, Any]) -> bool:
    if governance_decision.get("cross_core_integrity_passed") is True:
        return True

    if governance_decision.get("cross_core_passed") is True:
        return True

    stages = _safe_dict(governance_decision.get("stages"))
    cross_core = _safe_dict(stages.get("cross_core"))
    if cross_core.get("allowed") is True or cross_core.get("valid") is True:
        return True

    request = _safe_dict(governance_decision.get("request"))
    return bool(request.get("route") and request.get("target"))


def build_phase_closeout_pre_execution_context(
    *,
    request_id: str,
    actor: str,
    project_id: str,
    phase_id: str,
    client_email: str,
    governance_decision: Dict[str, Any],
    watcher_result: Optional[Dict[str, Any]] = None,
    state_result: Optional[Dict[str, Any]] = None,
    workflow_state: Optional[Dict[str, Any]] = None,
    phase_instance: Optional[Dict[str, Any]] = None,
    checklist_summary: Optional[Dict[str, Any]] = None,
    latest_signoff_status: Optional[Dict[str, Any]] = None,
    change_closeout_guard: Optional[Dict[str, Any]] = None,
    phase_closeout_gate: Optional[Dict[str, Any]] = None,
    receipt_planned: bool = True,
    operator_approved: bool = False,
) -> Dict[str, Any]:
    governor_passed = (
        governance_decision.get("allowed") is True
        or governance_decision.get("valid") is True
    )
    watcher_passed = _watcher_allowed(governance_decision, watcher_result)
    state_passed = _state_allowed(governance_decision, state_result)
    canon_passed = _canon_allowed(governance_decision)
    execution_gate_passed = _execution_gate_allowed(governance_decision)

    return {
        "artifact_type": "route_pre_execution_context",
        "artifact_version": ROUTE_EXECUTION_CONTEXT_VERSION,
        "generated_at": _utc_now_iso(),
        "request_id": request_id,
        "route": "/contractor-builder/phase-closeout/run",
        "method": "POST",
        "actor": actor,
        "target": "contractor_builder_v1.phase_closeout",
        "child_core_id": "contractor_builder_v1",
        "action_type": "phase_closeout",
        "action_class": "workflow_transition",
        "execution_intent": True,
        "project_id": project_id,
        "phase_id": phase_id,
        "governor_passed": governor_passed,
        "watcher_passed": watcher_passed,
        "state_passed": state_passed,
        "state_authority_passed": state_passed,
        "canon_passed": canon_passed,
        "execution_gate_passed": execution_gate_passed,
        "operator_approved": operator_approved,
        "receipt_planned": receipt_planned,
        "cross_core_integrity_passed": _cross_core_integrity_allowed(governance_decision),
        "cross_core_passed": _cross_core_integrity_allowed(governance_decision),
        "state_mutation_declared": True,
        "raw_input": False,
        "external_source": False,
        "source_type": "governed_route",
        "lineage": {
            "governance_decision_id": governance_decision.get("decision_id", ""),
            "request_governor_version": governance_decision.get("governor_version", ""),
            "watcher_status": _safe_dict(watcher_result).get("status", ""),
            "state_status": _safe_dict(state_result).get("status", ""),
            "canon_status": _safe_dict(
                _safe_dict(governance_decision.get("stages")).get("canon")
            ).get("status", ""),
            "execution_gate_status": _safe_dict(
                _safe_dict(governance_decision.get("stages")).get("execution_gate")
            ).get("status", ""),
            "research_packet_id": "route_state_authority_context",
            "interpretation_packet_id": "route_governor_context",
            "adapter_id": "contractor_phase_closeout_route_adapter",
        },
        "root_spine": {
            "spine_order": [
                "State Authority",
                "Watcher",
                "Canon",
                "Request Governor",
                "Execution Gate",
            ],
            "route_spine": [
                "workflow_state",
                "phase_instance",
                "checklist_summary",
                "change_closeout_guard",
                "phase_closeout_gate",
                "request_governor",
                "pre_execution_gate",
            ],
        },
        "payload": {
            "client_email": client_email,
            "receipt_planned": receipt_planned,
            "state_mutation_declared": True,
            "operator_approved": operator_approved,
        },
        "context": {
            "workflow_state": _safe_dict(workflow_state),
            "phase_instance": _safe_dict(phase_instance),
            "checklist_summary": _safe_dict(checklist_summary),
            "latest_signoff_status": _safe_dict(latest_signoff_status),
            "change_closeout_guard": _safe_dict(change_closeout_guard),
            "phase_closeout_gate": _safe_dict(phase_closeout_gate),
            "watcher_result": _safe_dict(watcher_result),
            "state_result": _safe_dict(state_result),
            "governance_decision": governance_decision,
        },
        "authority": {
            "ai_execution_authority": False,
            "memory_execution_authority": False,
            "system_brain_execution_authority": False,
            "watcher_override": False,
            "state_authority_override": False,
            "canon_override": False,
            "execution_gate_override": False,
            "governance_override": False,
            "bypass_execution_gate": False,
            "hidden_state_mutation": False,
        },
        "sealed": True,
    }
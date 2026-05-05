# AI_GO/core/governance/governance_explainer.py

from __future__ import annotations

from typing import Any, Dict, List


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _status(payload: Dict[str, Any]) -> str:
    return str(payload.get("status", "unknown")).strip() or "unknown"


def _valid(payload: Dict[str, Any]) -> bool:
    return payload.get("valid") is True or payload.get("allowed") is True


def explain_governance_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    governance_decision = _safe_dict(packet.get("governance_decision"))
    watcher = _safe_dict(packet.get("watcher"))
    state = _safe_dict(packet.get("state"))
    canon = _safe_dict(packet.get("canon"))
    execution_gate = _safe_dict(packet.get("execution_gate"))
    execution_result = _safe_dict(packet.get("execution_result"))

    watcher_errors = _safe_list(watcher.get("errors"))
    state_errors = _safe_list(state.get("errors"))
    gate_reasons = _safe_list(execution_gate.get("reasons"))

    allowed = execution_gate.get("allowed") is True

    if allowed:
        plain_summary = "The request passed watcher, state, canon, and execution gate checks. Execution was permitted."
    else:
        plain_summary = "The request did not clear governance. Execution should remain blocked."

    risk_flags: List[str] = []
    if watcher_errors:
        risk_flags.append("watcher_block")
    if state_errors:
        risk_flags.append("state_block")
    if gate_reasons:
        risk_flags.append("execution_gate_block")
    if execution_result.get("status") == "delivery_failed":
        risk_flags.append("delivery_failed")

    return {
        "status": "ok",
        "artifact_type": "governance_explanation",
        "mode": "observer_only",
        "execution_allowed": False,
        "plain_summary": plain_summary,
        "layer_read": {
            "governance_status": _status(governance_decision),
            "watcher_status": _status(watcher),
            "watcher_valid": _valid(watcher),
            "state_status": _status(state),
            "state_valid": _valid(state),
            "canon_status": _status(canon),
            "canon_valid": _valid(canon),
            "execution_gate_status": _status(execution_gate),
            "execution_gate_allowed": allowed,
            "execution_result_status": _status(execution_result),
        },
        "why_allowed_or_blocked": {
            "watcher_errors": watcher_errors,
            "state_errors": state_errors,
            "execution_gate_reasons": gate_reasons,
        },
        "what_changed": execution_result if execution_result else {},
        "risk_flags": risk_flags,
        "next_step": (
            "Proceed only with already-governed execution results."
            if allowed
            else "Fix the blocking governance layer before retrying execution."
        ),
        "authority_boundary": {
            "can_explain": True,
            "can_execute": False,
            "can_override_governance": False,
            "can_mutate_state": False,
        },
        "sealed": True,
    }
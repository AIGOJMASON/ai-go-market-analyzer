from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


EXECUTION_GATE_OPERATOR_SURFACE_VERSION = "v5G.4"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _authority() -> Dict[str, Any]:
    return {
        "operator_read_surface": True,
        "read_only": True,
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_state": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_state_authority": False,
        "can_override_canon": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_allow_request": False,
        "can_block_request": False,
        "execution_allowed": False,
        "mutation_allowed": False,
    }


def _use_policy() -> Dict[str, Any]:
    return {
        "operator_may_read": True,
        "pm_may_read": True,
        "system_brain_may_display": True,
        "dashboard_may_display": True,
        "may_change_execution_gate": False,
        "may_change_watcher": False,
        "may_change_state_authority": False,
        "may_change_canon": False,
        "may_change_runtime": False,
        "may_change_recommendations": False,
        "may_change_pm_strategy": False,
        "may_write_decisions": False,
        "may_dispatch_actions": False,
        "may_execute": False,
    }


def _derive_gate_value(decision: Dict[str, Any]) -> str:
    status = _safe_str(decision.get("status"))
    allowed = decision.get("allowed")

    if not decision:
        return "not_evaluated"

    if allowed is True or status == "passed":
        return "passed"

    if allowed is False or status == "blocked":
        return "blocked"

    return status or "unknown"


def _derive_meaning(value: str) -> str:
    if value == "passed":
        return "Execution Gate passed for the supplied governed decision. Visibility does not grant execution."
    if value == "blocked":
        return "Execution Gate blocked the supplied governed decision. Visibility does not perform blocking."
    if value == "not_evaluated":
        return "Execution Gate is installed, but no live decision was supplied to this read-only surface."
    return "Execution Gate posture is visible for operator awareness only."


def build_execution_gate_operator_surface(
    *,
    execution_gate_decision: Optional[Dict[str, Any]] = None,
    pre_execution_decision: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    pre_execution = _safe_dict(pre_execution_decision)
    gate_decision = _safe_dict(
        execution_gate_decision
        or pre_execution.get("execution_gate")
    )

    gate_value = _derive_gate_value(gate_decision)
    pre_value = _derive_gate_value(pre_execution)

    return {
        "artifact_type": "execution_gate_operator_surface",
        "artifact_version": EXECUTION_GATE_OPERATOR_SURFACE_VERSION,
        "generated_at": _utc_now_iso(),
        "status": "ok",
        "mode": "operator_read_only_surface",
        "sealed": True,
        "execution_gate": {
            "visible": True,
            "status": gate_value,
            "allowed": gate_decision.get("allowed"),
            "decision": gate_decision.get("decision", "not_evaluated"),
            "failed_checks": gate_decision.get("failed_checks", []),
            "passed_checks": gate_decision.get("passed_checks", []),
            "message": gate_decision.get("message", ""),
        },
        "pre_execution_gate": {
            "visible": bool(pre_execution),
            "status": pre_value,
            "allowed": pre_execution.get("allowed"),
            "decision": pre_execution.get("decision", "not_evaluated"),
        },
        "operator_card": {
            "card_id": "execution_gate",
            "label": "Execution Gate",
            "value": gate_value,
            "meaning": _derive_meaning(gate_value),
        },
        "what_to_watch": [
            "Execution Gate visibility is read-only. It cannot allow, block, execute, or mutate.",
            "If Execution Gate is blocked, inspect failed_checks and upstream Governor, Watcher, State Authority, and Canon stages.",
        ],
        "plain_summary": (
            "Execution Gate status is visible to the operator as read-only governance context. "
            "This surface grants no execution or mutation authority."
        ),
        "authority": _authority(),
        "use_policy": _use_policy(),
    }


def summarize_execution_gate_operator_surface(surface: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(surface)
    gate = _safe_dict(source.get("execution_gate"))

    return {
        "artifact_type": "execution_gate_operator_summary",
        "artifact_version": EXECUTION_GATE_OPERATOR_SURFACE_VERSION,
        "generated_at": _utc_now_iso(),
        "status": source.get("status", "unknown"),
        "mode": "read_only",
        "execution_gate_status": gate.get("status", "unknown"),
        "execution_gate_allowed": gate.get("allowed"),
        "plain_summary": source.get("plain_summary", ""),
        "operator_card": source.get("operator_card", {}),
        "authority": _authority(),
        "sealed": True,
    }
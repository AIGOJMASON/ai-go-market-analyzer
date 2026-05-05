from __future__ import annotations

from typing import Any, Dict

from AI_GO.core.execution_gate.execution_gate_policy import evaluate_execution_gate
from AI_GO.core.governance.cross_core_enforcer import evaluate_cross_core_handoff
from AI_GO.core.watcher.enforcement_watcher import record_enforcement_violation


PRE_EXECUTION_GATE_VERSION = "pre_execution_gate_v1.1"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def enforce_pre_execution_gate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Called immediately before any:
    - execution
    - state mutation
    - external call
    - delivery
    - child-core handoff that may influence governed output

    This wrapper combines:
    - Execution Gate authority decision
    - Cross-core handoff enforcement
    - Watcher escalation record on block
    """
    source = _safe_dict(context)

    gate_decision = evaluate_execution_gate(source)

    cross_core_packet = source.get("cross_core_packet")
    if cross_core_packet is None:
        cross_core_packet = source.get("handoff_packet")

    cross_core_decision: Dict[str, Any] = {
        "status": "not_run",
        "allowed": None,
        "reason": "No cross-core packet supplied.",
    }

    if isinstance(cross_core_packet, dict):
        cross_core_decision = evaluate_cross_core_handoff(cross_core_packet)

    cross_core_allowed = (
        cross_core_decision.get("allowed") is True
        or cross_core_decision.get("status") == "not_run"
    )

    allowed = gate_decision.get("allowed") is True and cross_core_allowed

    decision = {
        "artifact_type": "pre_execution_gate_decision",
        "artifact_version": PRE_EXECUTION_GATE_VERSION,
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "decision": "allow" if allowed else "block",
        "execution_gate": gate_decision,
        "cross_core_enforcement": cross_core_decision,
        "policy": {
            "execution_gate_required": True,
            "cross_core_enforcement_required_when_packet_supplied": True,
            "watcher_escalation_on_block": True,
        },
        "message": (
            "Pre-execution gate passed."
            if allowed
            else "Pre-execution gate blocked request."
        ),
    }

    if not allowed:
        violation = record_enforcement_violation(
            layer="pre_execution_gate",
            decision=decision,
            context=source,
        )

        raise PermissionError(
            {
                "error": "pre_execution_gate_blocked",
                "decision": decision,
                "watcher_violation": violation,
            }
        )

    return decision
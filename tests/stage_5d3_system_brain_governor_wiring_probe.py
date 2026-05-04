from __future__ import annotations

from typing import Any, Dict

from AI_GO.core.governance.request_governor import govern_request_from_dict
from AI_GO.core.system_brain.system_brain import build_system_brain_context


PHASE = "Phase 5D.3"
PROBE_ID = "stage_5d3_system_brain_governor_wiring_probe"


FORBIDDEN_TRUE_AUTHORITY_FLAGS = [
    "can_execute",
    "can_mutate_state",
    "can_mutate_source_artifacts",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_override_engines",
    "can_override_pm",
    "can_write_external_memory",
    "can_create_decision",
    "can_route_work",
    "can_block_request",
    "can_allow_request",
]


FORBIDDEN_TRUE_USE_FLAGS = [
    "may_change_canon_decision",
    "may_change_watcher",
    "may_change_execution_gate",
    "may_change_state",
    "may_write_decisions",
    "may_dispatch_actions",
    "may_activate_child_cores",
]


def _assert_system_brain_authority(system_brain: Dict[str, Any]) -> None:
    assert system_brain["artifact_type"] == "system_brain_context"
    assert system_brain["mode"] == "read_only"
    assert system_brain["sealed"] is True

    authority = system_brain.get("authority", {})
    assert isinstance(authority, dict)

    for key in FORBIDDEN_TRUE_AUTHORITY_FLAGS:
        assert authority.get(key) is False, f"{key} must remain false"

    use_policy = system_brain.get("use_policy", {})
    assert isinstance(use_policy, dict)

    for key in FORBIDDEN_TRUE_USE_FLAGS:
        assert use_policy.get(key) is False, f"{key} must remain false"


def _build_allowed_read_request() -> Dict[str, Any]:
    return {
        "request_id": "stage-5d3-read-allowed",
        "route": "/probe/read",
        "method": "GET",
        "actor": "stage_5d3_probe",
        "target": "system_brain_governor_wiring",
        "child_core_id": "contractor_builder_v1",
        "action_type": "read_system_brain",
        "action_class": "read",
        "payload": {},
        "context": {},
    }


def _build_blocked_execution_request() -> Dict[str, Any]:
    return {
        "request_id": "stage-5d3-execution-blocked",
        "route": "/probe/execute",
        "method": "POST",
        "actor": "stage_5d3_probe",
        "target": "system_brain_governor_wiring",
        "child_core_id": "contractor_builder_v1",
        "action_type": "execute",
        "action_class": "execute",
        "payload": {
            "state_mutation_declared": True,
            "receipt_planned": True,
            "operator_approved": True,
        },
        "context": {
            "watcher_result": {
                "status": "passed",
                "valid": True,
                "errors": [],
            },
            "watcher_passed": True,
            "state_mutation_declared": True,
            "receipt_planned": True,
            "operator_approved": True,
            "execution_gate_passed": False,
        },
    }


def run_probe() -> Dict[str, Any]:
    standalone_context = build_system_brain_context()
    _assert_system_brain_authority(standalone_context)

    allowed_decision = govern_request_from_dict(_build_allowed_read_request())

    assert allowed_decision["status"] == "passed"
    assert allowed_decision["allowed"] is True
    assert allowed_decision["valid"] is True
    assert "system_brain" in allowed_decision
    assert allowed_decision["stages"]["system_brain"]["status"] in {
        "available",
        "unavailable",
    }

    allowed_system_brain = allowed_decision["system_brain"]
    if allowed_decision["stages"]["system_brain"]["status"] == "available":
        _assert_system_brain_authority(allowed_system_brain)

    blocked_decision = govern_request_from_dict(_build_blocked_execution_request())

    assert blocked_decision["status"] == "blocked"
    assert blocked_decision["allowed"] is False
    assert blocked_decision["valid"] is False
    assert "system_brain" in blocked_decision

    blocked_codes = {
        reason.get("code")
        for reason in blocked_decision.get("rejection_reasons", [])
        if isinstance(reason, dict)
    }

    assert "canon_enforcement_blocked" in blocked_codes

    canon_stage = blocked_decision["stages"]["canon"]
    assert canon_stage["allowed"] is False

    canon_decision = canon_stage["decision"]
    canon_rejection_codes = {
        reason.get("code")
        for reason in canon_decision.get("rejection_reasons", [])
        if isinstance(reason, dict)
    }

    assert "execution_gate_required" in canon_rejection_codes

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "system_brain_context_available": standalone_context["artifact_type"]
        == "system_brain_context",
        "allowed_read_request_passed": allowed_decision["allowed"] is True,
        "blocked_execution_request_blocked": blocked_decision["allowed"] is False,
        "canon_remained_authoritative": "execution_gate_required"
        in canon_rejection_codes,
        "system_brain_authority_confirmed": "read_only_advisory_only",
        "next": {
            "phase": "5D.4",
            "recommended_step": "Add operator-facing System Brain visibility or build regression for posture warnings under degraded SMI conditions.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D3_SYSTEM_BRAIN_GOVERNOR_WIRING_PROBE: PASS")
    print(result)
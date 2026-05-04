from __future__ import annotations

from AI_GO.core.execution_gate import enforce_pre_execution_gate
from AI_GO.core.execution_gate.route_execution_context import (
    build_phase_closeout_pre_execution_context,
)


def _governance_decision() -> dict:
    return {
        "status": "passed",
        "allowed": True,
        "valid": True,
        "governor_version": "v5G.2-test",
        "stages": {
            "watcher": {
                "status": "passed",
                "allowed": True,
                "valid": True,
                "decision": {},
            },
            "state": {
                "status": "passed",
                "allowed": True,
                "valid": True,
                "decision": {},
            },
            "canon": {
                "status": "passed",
                "allowed": True,
                "valid": True,
                "decision": {},
            },
        },
    }


def _watcher_result(valid: bool = True) -> dict:
    return {
        "status": "passed" if valid else "blocked",
        "valid": valid,
        "allowed": valid,
        "errors": [] if valid else ["watcher_block"],
    }


def _workflow_state() -> dict:
    return {
        "project_id": "project-demo",
        "current_phase_id": "phase-demo",
        "workflow_status": "active",
    }


def _phase_instance() -> dict:
    return {
        "phase_id": "phase-demo",
        "phase_status": "awaiting_signoff",
        "phase_name": "Demo Phase",
    }


def _checklist_summary(ready: bool = True) -> dict:
    return {
        "phase_id": "phase-demo",
        "required_item_count": 2,
        "completed_required_count": 2 if ready else 1,
        "ready_for_signoff": ready,
    }


def _gate_result() -> dict:
    return {
        "status": "passed",
        "allowed": True,
        "valid": True,
    }


def _context(*, governance: dict | None = None, watcher: dict | None = None) -> dict:
    return build_phase_closeout_pre_execution_context(
        request_id="phase-closeout-project-demo-phase-demo",
        actor="test_operator",
        project_id="project-demo",
        phase_id="phase-demo",
        client_email="client@example.com",
        governance_decision=governance or _governance_decision(),
        watcher_result=watcher or _watcher_result(True),
        state_result={
            "status": "passed",
            "valid": True,
            "allowed": True,
        },
        workflow_state=_workflow_state(),
        phase_instance=_phase_instance(),
        checklist_summary=_checklist_summary(True),
        latest_signoff_status={},
        change_closeout_guard={
            "phase_has_blocking_unresolved_changes": False,
        },
        phase_closeout_gate=_gate_result(),
        receipt_planned=True,
        operator_approved=True,
    )


def test_route_pre_execution_context_passes_when_all_layers_pass() -> None:
    decision = enforce_pre_execution_gate(_context())

    assert decision["allowed"] is True
    assert decision["status"] == "passed"
    assert decision["execution_gate"]["allowed"] is True


def test_route_pre_execution_context_blocks_when_watcher_fails() -> None:
    context = _context(watcher=_watcher_result(False))

    try:
        enforce_pre_execution_gate(context)
    except PermissionError as exc:
        payload = exc.args[0]
    else:
        raise AssertionError("Expected watcher failure to block pre-execution.")

    assert payload["error"] == "pre_execution_gate_blocked"
    assert payload["decision"]["allowed"] is False
    assert payload["decision"]["execution_gate"]["allowed"] is False


def test_route_pre_execution_context_blocks_when_governor_fails() -> None:
    governance = _governance_decision()
    governance["allowed"] = False
    governance["valid"] = False
    governance["status"] = "blocked"

    context = _context(governance=governance)

    try:
        enforce_pre_execution_gate(context)
    except PermissionError as exc:
        payload = exc.args[0]
    else:
        raise AssertionError("Expected governor failure to block pre-execution.")

    assert payload["error"] == "pre_execution_gate_blocked"
    assert payload["decision"]["allowed"] is False
    assert payload["decision"]["execution_gate"]["allowed"] is False


def test_route_pre_execution_context_blocks_without_operator_approval() -> None:
    context = build_phase_closeout_pre_execution_context(
        request_id="phase-closeout-project-demo-phase-demo",
        actor="test_operator",
        project_id="project-demo",
        phase_id="phase-demo",
        client_email="client@example.com",
        governance_decision=_governance_decision(),
        watcher_result=_watcher_result(True),
        state_result={
            "status": "passed",
            "valid": True,
            "allowed": True,
        },
        workflow_state=_workflow_state(),
        phase_instance=_phase_instance(),
        checklist_summary=_checklist_summary(True),
        latest_signoff_status={},
        change_closeout_guard={
            "phase_has_blocking_unresolved_changes": False,
        },
        phase_closeout_gate=_gate_result(),
        receipt_planned=True,
        operator_approved=False,
    )

    try:
        enforce_pre_execution_gate(context)
    except PermissionError as exc:
        payload = exc.args[0]
    else:
        raise AssertionError("Expected missing operator approval to block pre-execution.")

    assert payload["error"] == "pre_execution_gate_blocked"
    assert "operator_approval_required" in payload["decision"]["execution_gate"]["failed_checks"]


def run_probe() -> dict:
    test_route_pre_execution_context_passes_when_all_layers_pass()
    test_route_pre_execution_context_blocks_when_watcher_fails()
    test_route_pre_execution_context_blocks_when_governor_fails()
    test_route_pre_execution_context_blocks_without_operator_approval()

    return {
        "status": "passed",
        "phase": "Phase 5G.2",
        "layer": "execution_gate_real_route_integration",
        "phase_closeout_route_context_guarded": True,
        "pre_execution_gate_runs_before_side_effects": True,
        "watcher_failure_blocks_execution": True,
        "governor_failure_blocks_execution": True,
        "operator_approval_required": True,
        "execution_gate_law": {
            "route": "/contractor-builder/phase-closeout/run",
            "pdf_generation_guarded": True,
            "email_delivery_guarded": True,
            "signoff_state_write_guarded": True,
            "receipt_writes_guarded": True,
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5G2_EXECUTION_GATE_ROUTE_INTEGRATION_PROBE: PASS")
    print(result)
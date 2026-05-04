from __future__ import annotations

from AI_GO.core.canon_runtime.canon_enforcer import enforce_canon_action_from_dict


def test_blocks_legacy_execute_without_gate() -> None:
    decision = enforce_canon_action_from_dict(
        {
            "action_type": "execute",
            "action_class": "execute",
            "actor": "test_operator",
            "target": "contractor_builder_v1",
            "payload": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
            },
            "context": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
                "execution_gate_passed": False,
            },
        }
    )

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"

    codes = {reason["code"] for reason in decision["rejection_reasons"]}
    assert "execution_gate_required" in codes


def test_blocks_phase_closeout_without_checklist() -> None:
    decision = enforce_canon_action_from_dict(
        {
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "actor": "test_operator",
            "target": "phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "project_id": "project-demo",
            "phase_id": "phase-demo-inspection",
            "payload": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
            },
            "context": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
                "workflow_state": {
                    "current_phase_id": "phase-demo-inspection",
                },
                "phase_instance": {
                    "phase_status": "awaiting_signoff",
                },
                "checklist_summary": {
                    "ready_for_signoff": False,
                },
            },
        }
    )

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"

    codes = {reason["code"] for reason in decision["rejection_reasons"]}
    assert "checklist_not_ready" in codes


def test_allows_ai_proposal_with_bounded_context() -> None:
    decision = enforce_canon_action_from_dict(
        {
            "action_type": "ai_propose",
            "action_class": "read",
            "actor": "test_operator",
            "target": "contractor_builder_v1",
            "context": {
                "bounded_context": True,
            },
            "payload": {
                "declared_intent": "propose next governed action only",
            },
        }
    )

    assert decision["allowed"] is True
    assert decision["status"] == "passed"


def test_blocks_ai_execution_action_type() -> None:
    decision = enforce_canon_action_from_dict(
        {
            "action_type": "autonomous_agent",
            "action_class": "execute",
            "actor": "test_operator",
            "target": "contractor_builder_v1",
            "context": {
                "bounded_context": True,
            },
        }
    )

    assert decision["allowed"] is False

    codes = {reason["code"] for reason in decision["rejection_reasons"]}
    assert "hard_blocked_action_type" in codes


def test_allows_phase_closeout_when_canon_conditions_pass() -> None:
    decision = enforce_canon_action_from_dict(
        {
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "actor": "test_operator",
            "target": "phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "project_id": "project-demo",
            "phase_id": "phase-demo-inspection",
            "payload": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
            },
            "context": {
                "state_mutation_declared": True,
                "watcher_passed": True,
                "receipt_planned": True,
                "operator_approved": True,
                "workflow_state": {
                    "current_phase_id": "phase-demo-inspection",
                },
                "phase_instance": {
                    "phase_status": "awaiting_signoff",
                },
                "checklist_summary": {
                    "ready_for_signoff": True,
                },
            },
        }
    )

    assert decision["allowed"] is True
    assert decision["status"] == "passed"
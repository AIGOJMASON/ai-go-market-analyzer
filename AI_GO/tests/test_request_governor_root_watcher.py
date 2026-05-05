from __future__ import annotations

from typing import Any, Dict

import AI_GO.core.governance.request_governor as request_governor


def _fake_state_pass(*, phase_status: str = "awaiting_signoff") -> Dict[str, Any]:
    return {
        "status": "passed",
        "allowed": True,
        "valid": True,
        "state_required": True,
        "state_passed": True,
        "errors": [],
        "warnings": [],
        "state_validation": {
            "project_id": "project-demo",
            "matched_phase": {
                "phase_id": "phase-demo-inspection",
                "phase_status": phase_status,
                "phase_name": "Inspection",
            },
            "state_context": {
                "workflow_state": {
                    "project_id": "project-demo",
                    "current_phase_id": "phase-demo-inspection",
                },
                "phase_instances": [
                    {
                        "phase_id": "phase-demo-inspection",
                        "phase_status": phase_status,
                        "phase_name": "Inspection",
                    }
                ],
            },
        },
    }


def test_request_governor_blocks_at_root_watcher_before_canon(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        request_governor,
        "build_state_authority_packet",
        lambda payload: _fake_state_pass(phase_status="in_progress"),
    )

    decision = request_governor.govern_request_from_dict(
        {
            "request_id": "watcher-block-demo",
            "route": "/contractor-builder/phase-closeout/run",
            "method": "POST",
            "actor": "test_operator",
            "target": "contractor_builder_v1.phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": "project-demo",
            "phase_id": "phase-demo-inspection",
            "payload": {
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
            },
            "context": {
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
                "checklist_summary": {
                    "ready_for_signoff": True,
                },
                "change_closeout_guard": {
                    "phase_has_blocking_unresolved_changes": False,
                },
            },
        }
    )

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"

    codes = {reason["code"] for reason in decision["rejection_reasons"]}
    assert "watcher_blocked" in codes

    assert decision["stages"]["state"]["allowed"] is True
    assert decision["stages"]["watcher"]["allowed"] is False
    assert "phase_not_awaiting_signoff" in decision["stages"]["watcher"]["decision"]["errors"]
    assert decision["stages"]["canon"]["status"] == "not_run"
    assert decision["stages"]["execution_gate"]["status"] == "not_required"


def test_request_governor_allows_after_root_watcher_passes(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        request_governor,
        "build_state_authority_packet",
        lambda payload: _fake_state_pass(phase_status="awaiting_signoff"),
    )

    decision = request_governor.govern_request_from_dict(
        {
            "request_id": "watcher-pass-demo",
            "route": "/contractor-builder/phase-closeout/run",
            "method": "POST",
            "actor": "test_operator",
            "target": "contractor_builder_v1.phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": "project-demo",
            "phase_id": "phase-demo-inspection",
            "payload": {
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
                "cross_core_integrity_passed": True,
            },
            "context": {
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
                "cross_core_integrity_passed": True,
                "checklist_summary": {
                    "ready_for_signoff": True,
                },
                "change_closeout_guard": {
                    "phase_has_blocking_unresolved_changes": False,
                },
            },
        }
    )

    assert decision["allowed"] is True
    assert decision["status"] == "passed"
    assert decision["stages"]["state"]["allowed"] is True
    assert decision["stages"]["watcher"]["allowed"] is True
    assert decision["stages"]["canon"]["allowed"] is True
    assert decision["stages"]["execution_gate"]["allowed"] is True
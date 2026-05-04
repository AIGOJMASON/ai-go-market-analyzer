from __future__ import annotations

from AI_GO.core.governance.request_governor import govern_request_from_dict


def test_request_governor_blocks_missing_project_id_before_canon() -> None:
    decision = govern_request_from_dict(
        {
            "request_id": "state-authority-missing-project",
            "route": "/contractor-builder/phase-closeout/run",
            "method": "POST",
            "actor": "test_operator",
            "target": "contractor_builder_v1.phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": "",
            "phase_id": "phase-demo",
            "payload": {
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
            },
            "context": {
                "watcher_passed": True,
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": True,
            },
        }
    )

    assert decision["allowed"] is False
    assert decision["status"] == "blocked"
    assert decision["decision"] == "block"

    codes = {reason["code"] for reason in decision["rejection_reasons"]}
    assert "state_authority_blocked" in codes

    assert decision["stages"]["state"]["allowed"] is False
    assert decision["stages"]["canon"]["status"] == "not_run"
    assert decision["stages"]["execution_gate"]["status"] == "not_required"


def test_request_governor_allows_read_when_state_not_required() -> None:
    decision = govern_request_from_dict(
        {
            "request_id": "state-authority-read",
            "route": "/contractor-builder/project-record/read",
            "method": "POST",
            "actor": "test_operator",
            "target": "contractor_builder_v1.project_record",
            "child_core_id": "contractor_builder_v1",
            "action_type": "read_project_record",
            "action_class": "read",
            "project_id": "",
            "phase_id": "",
            "payload": {},
            "context": {},
        }
    )

    assert decision["allowed"] is True
    assert decision["status"] == "passed"
    assert decision["stages"]["state"]["allowed"] is True
    assert decision["stages"]["state"]["decision"]["state_required"] is False
    assert decision["stages"]["execution_gate"]["status"] == "not_required"
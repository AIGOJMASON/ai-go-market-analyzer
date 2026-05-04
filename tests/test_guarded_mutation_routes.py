from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi import HTTPException

import AI_GO.api.contractor_decision_api as decision_api
import AI_GO.api.contractor_change_api as change_api
import AI_GO.api.contractor_assumption_api as assumption_api
import AI_GO.api.contractor_workflow_api as workflow_api


def _blocked_guard(**kwargs: Any) -> Dict[str, Any]:
    raise PermissionError(
        {
            "error": "mutation_guard_blocked",
            "governance_decision": {
                "status": "blocked",
                "allowed": False,
                "rejection_reasons": [
                    {
                        "code": "probe_forced_block",
                        "message": "Probe forced guard block.",
                    }
                ],
            },
        }
    )


def test_decision_create_blocks_before_service(monkeypatch: Any) -> None:
    service_called = {"value": False}

    def fake_create_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["value"] = True
        return {"status": "should_not_happen"}

    monkeypatch.setattr(decision_api, "require_governed_mutation", _blocked_guard)
    monkeypatch.setattr(decision_api, "create_decision", fake_create_decision)

    with pytest.raises(HTTPException) as exc:
        decision_api.create_decision_entry(
            decision_api.DecisionCreateRequest(
                entry_kwargs={
                    "project_id": "project-demo",
                    "phase_id": "phase-demo",
                    "title": "Probe decision",
                },
                operator_approved=True,
            )
        )

    assert exc.value.status_code == 403
    assert service_called["value"] is False


def test_change_transition_blocks_before_service(monkeypatch: Any) -> None:
    service_called = {"value": False}

    def fake_transition_change_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["value"] = True
        return {"status": "should_not_happen"}

    monkeypatch.setattr(change_api, "require_governed_mutation", _blocked_guard)
    monkeypatch.setattr(change_api, "transition_change_packet", fake_transition_change_packet)

    with pytest.raises(HTTPException) as exc:
        change_api.transition_change_packet_route(
            change_api.ChangeStatusRequest(
                packet={
                    "project_id": "project-demo",
                    "phase_id": "phase-demo",
                    "change_packet_id": "change-demo",
                },
                new_status="approved",
                operator_approved=True,
            )
        )

    assert exc.value.status_code == 403
    assert service_called["value"] is False


def test_assumption_invalidate_blocks_before_service(monkeypatch: Any) -> None:
    service_called = {"value": False}

    def fake_invalidate_assumption(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["value"] = True
        return {"status": "should_not_happen"}

    monkeypatch.setattr(assumption_api, "require_governed_mutation", _blocked_guard)
    monkeypatch.setattr(assumption_api, "invalidate_assumption", fake_invalidate_assumption)

    with pytest.raises(HTTPException) as exc:
        assumption_api.invalidate_assumption_entry(
            assumption_api.AssumptionInvalidateRequest(
                entry={
                    "project_id": "project-demo",
                    "phase_id": "phase-demo",
                    "assumption_id": "assumption-demo",
                },
                actor_name="Tester",
                actor_role="PM",
                conversion_option="convert_to_decision",
                rationale="Probe invalidation.",
                operator_approved=True,
            )
        )

    assert exc.value.status_code == 403
    assert service_called["value"] is False


def test_workflow_repair_blocks_before_service(monkeypatch: Any) -> None:
    service_called = {"value": False}

    def fake_repair_upsert_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["value"] = True
        return {"status": "should_not_happen"}

    monkeypatch.setattr(workflow_api, "require_governed_mutation", _blocked_guard)
    monkeypatch.setattr(workflow_api, "repair_upsert_workflow", fake_repair_upsert_workflow)

    with pytest.raises(HTTPException) as exc:
        workflow_api.repair_upsert_contractor_workflow(
            workflow_api.WorkflowRepairUpsertRequest(
                project_id="project-demo",
                phase_instances=[
                    {
                        "phase_id": "phase-demo",
                        "phase_status": "awaiting_signoff",
                    }
                ],
                operator_approved=True,
            )
        )

    assert exc.value.status_code == 403
    assert service_called["value"] is False


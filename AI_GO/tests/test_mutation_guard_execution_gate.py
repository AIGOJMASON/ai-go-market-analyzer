from __future__ import annotations

from typing import Any, Dict

import pytest

import AI_GO.core.governance.mutation_guard as mutation_guard


def test_mutation_guard_blocks_when_governor_blocks(monkeypatch: Any) -> None:
    def fake_governor(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "blocked",
            "allowed": False,
            "valid": False,
            "stages": {
                "execution_gate": {
                    "status": "not_run",
                    "allowed": None,
                    "decision": {},
                }
            },
            "rejection_reasons": [
                {
                    "code": "state_authority_blocked",
                    "message": "blocked",
                }
            ],
        }

    monkeypatch.setattr(mutation_guard, "govern_request_from_dict", fake_governor)

    with pytest.raises(PermissionError) as exc:
        mutation_guard.require_governed_mutation(
            request_id="test-blocked",
            route="/contractor-builder/decision/create",
            method="POST",
            actor="test_operator",
            target="contractor_builder_v1.decision",
            child_core_id="contractor_builder_v1",
            action_type="create_decision",
            action_class="write_state",
            project_id="project-demo",
            payload={"receipt_planned": True, "operator_approved": True},
            context={"receipt_planned": True, "operator_approved": True},
        )

    assert exc.value.args[0]["error"] == "mutation_guard_blocked"


def test_mutation_guard_blocks_when_execution_gate_missing(monkeypatch: Any) -> None:
    def fake_governor(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "passed",
            "allowed": True,
            "valid": True,
            "stages": {
                "execution_gate": {
                    "status": "not_required",
                    "allowed": None,
                    "decision": {},
                }
            },
        }

    monkeypatch.setattr(mutation_guard, "govern_request_from_dict", fake_governor)

    with pytest.raises(PermissionError) as exc:
        mutation_guard.require_governed_mutation(
            request_id="test-no-gate",
            route="/contractor-builder/decision/create",
            method="POST",
            actor="test_operator",
            target="contractor_builder_v1.decision",
            child_core_id="contractor_builder_v1",
            action_type="create_decision",
            action_class="write_state",
            project_id="project-demo",
            payload={"receipt_planned": True, "operator_approved": True},
            context={"receipt_planned": True, "operator_approved": True},
        )

    assert exc.value.args[0]["error"] == "mutation_guard_execution_gate_not_passed"


def test_mutation_guard_allows_only_after_execution_gate_passes(monkeypatch: Any) -> None:
    captured: Dict[str, Any] = {}

    def fake_governor(payload: Dict[str, Any]) -> Dict[str, Any]:
        captured.update(payload)

        return {
            "status": "passed",
            "allowed": True,
            "valid": True,
            "stages": {
                "execution_gate": {
                    "status": "passed",
                    "allowed": True,
                    "decision": {
                        "allowed": True,
                    },
                }
            },
        }

    monkeypatch.setattr(mutation_guard, "govern_request_from_dict", fake_governor)

    result = mutation_guard.require_governed_mutation(
        request_id="test-pass",
        route="/contractor-builder/decision/create",
        method="POST",
        actor="test_operator",
        target="contractor_builder_v1.decision",
        child_core_id="contractor_builder_v1",
        action_type="create_decision",
        action_class="write_state",
        project_id="project-demo",
        payload={"receipt_planned": True, "operator_approved": True},
        context={"receipt_planned": True, "operator_approved": True},
    )

    assert result["allowed"] is True
    assert captured["context"]["execution_intent"] is True
    assert captured["context"]["state_mutation_declared"] is True
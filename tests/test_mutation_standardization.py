from __future__ import annotations

from typing import Any, Dict

import pytest

import AI_GO.core.governance.mutation_guard as mutation_guard


def test_mutation_guard_blocks_without_receipt_planned() -> None:
    with pytest.raises(PermissionError) as exc:
        mutation_guard.require_governed_mutation(
            request_id="missing-receipt",
            route="/contractor-builder/decision/create",
            method="POST",
            actor="test_operator",
            target="contractor_builder_v1.decision",
            child_core_id="contractor_builder_v1",
            action_type="create_decision",
            action_class="write_state",
            project_id="project-demo",
            payload={"operator_approved": True},
            context={"operator_approved": True},
        )

    assert exc.value.args[0]["error"] == "mutation_standard_missing_receipt_planned"


def test_mutation_guard_blocks_without_operator_approval() -> None:
    with pytest.raises(PermissionError) as exc:
        mutation_guard.require_governed_mutation(
            request_id="missing-approval",
            route="/contractor-builder/decision/create",
            method="POST",
            actor="test_operator",
            target="contractor_builder_v1.decision",
            child_core_id="contractor_builder_v1",
            action_type="create_decision",
            action_class="write_state",
            project_id="project-demo",
            payload={"receipt_planned": True},
            context={"receipt_planned": True},
        )

    assert exc.value.args[0]["error"] == "mutation_standard_missing_operator_approved"


def test_mutation_guard_blocks_bypass_execution_gate() -> None:
    with pytest.raises(PermissionError) as exc:
        mutation_guard.require_governed_mutation(
            request_id="bypass-gate",
            route="/contractor-builder/decision/create",
            method="POST",
            actor="test_operator",
            target="contractor_builder_v1.decision",
            child_core_id="contractor_builder_v1",
            action_type="create_decision",
            action_class="write_state",
            project_id="project-demo",
            payload={
                "receipt_planned": True,
                "operator_approved": True,
                "bypass_execution_gate": True,
            },
            context={
                "receipt_planned": True,
                "operator_approved": True,
            },
        )

    assert exc.value.args[0]["error"] == "mutation_standard_bypass_execution_gate"


def test_mutation_guard_passes_standardized_payload_to_governor(monkeypatch: Any) -> None:
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
        request_id="standardized",
        route="/contractor-builder/decision/create",
        method="POST",
        actor="test_operator",
        target="contractor_builder_v1.decision",
        child_core_id="contractor_builder_v1",
        action_type="create_decision",
        action_class="write_state",
        project_id="project-demo",
        payload={
            "receipt_planned": True,
            "operator_approved": True,
        },
        context={
            "receipt_planned": True,
            "operator_approved": True,
        },
    )

    assert result["allowed"] is True
    assert result["mutation_guard_version"] == "mutation_guard_v1.1"

    assert captured["payload"]["execution_intent"] is True
    assert captured["payload"]["state_mutation_declared"] is True
    assert captured["payload"]["receipt_planned"] is True
    assert captured["payload"]["operator_approved"] is True

    assert captured["context"]["execution_intent"] is True
    assert captured["context"]["state_mutation_declared"] is True
    assert captured["context"]["receipt_planned"] is True
    assert captured["context"]["operator_approved"] is True
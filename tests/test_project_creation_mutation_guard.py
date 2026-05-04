from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi import HTTPException

import AI_GO.api.contractor_projects_api as projects_api


def _request() -> projects_api.ContractorProjectCreateRequest:
    return projects_api.ContractorProjectCreateRequest(
        project_name="Demo Kitchen Remodel",
        project_type="Kitchen Remodel",
        client_name="Demo Client",
        pm_name="Demo PM",
        jurisdiction={"state": "IN", "authority_name": "Demo Authority"},
        baseline_refs={"schedule": "schedule-demo", "budget": "budget-demo"},
        operator_approved=True,
        receipt_planned=True,
    )


def test_project_creation_blocks_before_project_state_write(monkeypatch: Any) -> None:
    service_called = {"profile": False, "baseline": False, "receipt": False}

    def blocked_guard(**kwargs: Any) -> Dict[str, Any]:
        raise PermissionError(
            {
                "error": "mutation_guard_blocked",
                "governance_decision": {
                    "status": "blocked",
                    "allowed": False,
                },
            }
        )

    def fake_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["profile"] = True
        return {"project_id": "should-not-write"}

    def fake_baseline(payload: Dict[str, Any]) -> Dict[str, Any]:
        service_called["baseline"] = True
        return {"project_id": "should-not-write"}

    def fake_receipt(receipt: Dict[str, Any]) -> str:
        service_called["receipt"] = True
        return "should-not-write"

    monkeypatch.setattr(projects_api, "require_governed_mutation", blocked_guard)
    monkeypatch.setattr(projects_api, "create_project_profile_record", fake_profile)
    monkeypatch.setattr(projects_api, "create_baseline_lock_record", fake_baseline)
    monkeypatch.setattr(projects_api, "write_project_intake_receipt", fake_receipt)

    with pytest.raises(HTTPException) as exc:
        projects_api.create_contractor_project(_request())

    assert exc.value.status_code == 403
    assert service_called == {
        "profile": False,
        "baseline": False,
        "receipt": False,
    }


def test_project_creation_calls_guard_before_writes(monkeypatch: Any) -> None:
    guard_called = {"value": False}

    def passing_guard(**kwargs: Any) -> Dict[str, Any]:
        guard_called["value"] = True
        assert kwargs["action_type"] == "create_contractor_project"
        assert kwargs["action_class"] == "write_state"
        assert kwargs["context"]["receipt_planned"] is True
        assert kwargs["context"]["operator_approved"] is True
        assert kwargs["context"]["state_mutation_declared"] is True
        return {"status": "passed", "allowed": True, "valid": True}

    def fake_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
        assert guard_called["value"] is True
        return {
            "project_id": "project-demo",
            "project_name": "Demo Kitchen Remodel",
            "artifact_path": "profile.json",
        }

    def fake_baseline(payload: Dict[str, Any]) -> Dict[str, Any]:
        assert guard_called["value"] is True
        return {
            "project_id": "project-demo",
            "artifact_path": "baseline.json",
        }

    def fake_receipt(**kwargs: Any) -> Dict[str, Any]:
        assert guard_called["value"] is True
        return {"receipt_id": "receipt-demo"}

    def fake_write(receipt: Dict[str, Any]) -> str:
        assert guard_called["value"] is True
        return "receipt.json"

    monkeypatch.setattr(projects_api, "require_governed_mutation", passing_guard)
    monkeypatch.setattr(projects_api, "create_project_profile_record", fake_profile)
    monkeypatch.setattr(projects_api, "create_baseline_lock_record", fake_baseline)
    monkeypatch.setattr(projects_api, "build_project_intake_receipt", fake_receipt)
    monkeypatch.setattr(projects_api, "write_project_intake_receipt", fake_write)

    result = projects_api.create_contractor_project(_request())

    assert result["status"] == "created"
    assert result["mutation_guard"]["allowed"] is True
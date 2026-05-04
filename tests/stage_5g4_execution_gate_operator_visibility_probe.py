from __future__ import annotations

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.execution_gate.execution_gate_operator_surface import (
    build_execution_gate_operator_surface,
    summarize_execution_gate_operator_surface,
)


def _sample_execution_gate_decision(allowed: bool = False) -> dict:
    return {
        "artifact_type": "execution_gate_decision",
        "artifact_version": "v5G.1",
        "status": "passed" if allowed else "blocked",
        "allowed": allowed,
        "valid": allowed,
        "decision": "allow" if allowed else "block",
        "failed_checks": [] if allowed else ["operator_approval_required"],
        "passed_checks": ["governor_required", "watcher_required"],
        "message": "sample decision",
    }


def test_execution_gate_operator_surface_is_read_only() -> None:
    surface = build_execution_gate_operator_surface(
        execution_gate_decision=_sample_execution_gate_decision(False)
    )

    assert surface["artifact_type"] == "execution_gate_operator_surface"
    assert surface["mode"] == "operator_read_only_surface"
    assert surface["sealed"] is True
    assert surface["execution_gate"]["status"] == "blocked"

    assert surface["authority"]["read_only"] is True
    assert surface["authority"]["advisory_only"] is True
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_mutate_state"] is False
    assert surface["authority"]["can_override_execution_gate"] is False
    assert surface["authority"]["can_allow_request"] is False
    assert surface["authority"]["can_block_request"] is False
    assert surface["authority"]["execution_allowed"] is False
    assert surface["authority"]["mutation_allowed"] is False

    assert surface["use_policy"]["may_execute"] is False
    assert surface["use_policy"]["may_dispatch_actions"] is False
    assert surface["use_policy"]["may_write_decisions"] is False


def test_execution_gate_operator_summary_is_read_only() -> None:
    surface = build_execution_gate_operator_surface(
        execution_gate_decision=_sample_execution_gate_decision(True)
    )
    summary = summarize_execution_gate_operator_surface(surface)

    assert summary["artifact_type"] == "execution_gate_operator_summary"
    assert summary["mode"] == "read_only"
    assert summary["execution_gate_status"] == "passed"
    assert summary["execution_gate_allowed"] is True
    assert summary["authority"]["can_execute"] is False
    assert summary["authority"]["can_mutate_state"] is False


def test_execution_gate_api_surface_is_visible_and_non_authoritative() -> None:
    client = TestClient(app)

    response = client.get("/contractor-builder/system-brain/execution-gate/surface")
    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    surface = payload["surface"]
    assert surface["artifact_type"] == "execution_gate_operator_surface"
    assert surface["authority"]["can_execute"] is False
    assert surface["authority"]["can_allow_request"] is False
    assert surface["authority"]["can_block_request"] is False


def test_system_brain_surface_includes_execution_gate_panel() -> None:
    client = TestClient(app)

    response = client.get("/contractor-builder/system-brain/surface?limit=10")
    assert response.status_code == 200

    payload = response.json()
    surface = payload["surface"]

    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert "execution_gate_panel" in surface
    assert "execution_gate" in payload

    panel = surface["execution_gate_panel"]
    assert panel["artifact_type"] == "execution_gate_operator_surface"
    assert panel["authority"]["can_execute"] is False
    assert panel["authority"]["can_mutate_state"] is False
    assert panel["authority"]["can_override_execution_gate"] is False


def run_probe() -> dict:
    test_execution_gate_operator_surface_is_read_only()
    test_execution_gate_operator_summary_is_read_only()
    test_execution_gate_api_surface_is_visible_and_non_authoritative()
    test_system_brain_surface_includes_execution_gate_panel()

    return {
        "status": "passed",
        "phase": "Phase 5G.4",
        "layer": "execution_gate_operator_visibility",
        "execution_gate_surface_visible": True,
        "execution_gate_summary_visible": True,
        "system_brain_panel_present": True,
        "operator_visibility_read_only": True,
        "execution_authority_granted": False,
        "mutation_authority_granted": False,
        "can_allow_or_block_from_visibility": False,
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5G4_EXECUTION_GATE_OPERATOR_VISIBILITY_PROBE: PASS")
    print(result)
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.state_runtime.state_authority import build_state_authority_packet


PHASE = "5E.3"
PROBE_ID = "stage_5e3_state_authority_visibility_probe"

PROJECT_ID = "project-stage_5e3_state_authority_visibility_probe"
PHASE_ID = "phase-stage_5e3_closeout"


FORBIDDEN_AUTHORITY_TRUE = [
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "can_create_decision",
    "can_dispatch",
    "execution_allowed",
    "mutation_allowed",
]


FORBIDDEN_USE_TRUE = [
    "may_change_state",
    "may_execute",
    "may_dispatch",
    "may_override_governance",
    "may_override_watcher",
    "may_override_execution_gate",
]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _prepare_project_state() -> Dict[str, str]:
    root = (
        Path("AI_GO")
        / "state"
        / "contractor_builder_v1"
        / "projects"
        / "by_project"
        / PROJECT_ID
    )
    workflow_root = root / "workflow"

    _write_json(
        root / "project_profile.json",
        {
            "project_id": PROJECT_ID,
            "project_name": "Stage 5E.3 State Authority Visibility Probe",
        },
    )

    _write_json(
        root / "baseline_lock.json",
        {
            "project_id": PROJECT_ID,
            "baseline_locked": True,
        },
    )

    _write_json(
        workflow_root / "workflow_state.json",
        {
            "project_id": PROJECT_ID,
            "workflow_status": "active",
            "current_phase_id": PHASE_ID,
        },
    )

    _write_json(
        workflow_root / "phase_instances.json",
        [
            {
                "project_id": PROJECT_ID,
                "phase_id": PHASE_ID,
                "phase_name": "Closeout",
                "phase_status": "awaiting_signoff",
            }
        ],
    )

    _write_json(
        workflow_root / "checklists.json",
        {
            PHASE_ID: [
                {
                    "item_id": "inspection-complete",
                    "label": "Inspection complete",
                    "required": True,
                    "completed": True,
                }
            ]
        },
    )

    return {
        "project_root": str(root),
        "workflow_root": str(workflow_root),
    }


def _state_request(
    *,
    project_id: str = PROJECT_ID,
    phase_id: str = PHASE_ID,
) -> Dict[str, Any]:
    return {
        "action_type": "phase_closeout",
        "action_class": "workflow_transition",
        "project_id": project_id,
        "phase_id": phase_id,
        "payload": {},
        "context": {},
    }


def _assert_no_authority(packet: Dict[str, Any]) -> None:
    authority = packet["authority"]
    use_policy = packet["use_policy"]

    assert authority["mode"] == "state_verification_only"
    assert authority["read_only"] is True
    assert authority["can_verify_state"] is True

    for key in FORBIDDEN_AUTHORITY_TRUE:
        assert authority.get(key) is False, f"authority.{key} must remain false"

    for key in FORBIDDEN_USE_TRUE:
        assert use_policy.get(key) is False, f"use_policy.{key} must remain false"

    assert packet["validation"]["valid"] is True
    assert packet["validation"]["authority_violations"] == []


def run_probe() -> Dict[str, Any]:
    paths = _prepare_project_state()

    direct_packet = build_state_authority_packet(_state_request())
    _assert_no_authority(direct_packet)

    assert direct_packet["status"] == "passed"
    assert direct_packet["state_passed"] is True

    client = TestClient(app)

    health = client.get("/contractor-builder/health")
    assert health.status_code == 200, health.text
    health_payload = health.json()
    assert health_payload["routes"]["state_authority"] is True

    check_response = client.post(
        "/contractor-builder/state-authority/check",
        json=_state_request(),
    )
    assert check_response.status_code == 200, check_response.text

    check_payload = check_response.json()
    assert check_payload["status"] == "ok"
    assert check_payload["mode"] == "read_only"
    assert check_payload["execution_allowed"] is False
    assert check_payload["mutation_allowed"] is False

    api_packet = check_payload["state_authority"]
    _assert_no_authority(api_packet)

    assert api_packet["status"] == "passed"
    assert api_packet["state_passed"] is True
    assert check_payload["summary"]["state_passed"] is True
    assert check_payload["summary"]["execution_allowed"] is False
    assert check_payload["summary"]["mutation_allowed"] is False

    wrong_phase_response = client.post(
        "/contractor-builder/state-authority/check",
        json=_state_request(phase_id="phase-not-current"),
    )
    assert wrong_phase_response.status_code == 200, wrong_phase_response.text

    wrong_phase_payload = wrong_phase_response.json()
    wrong_phase_packet = wrong_phase_payload["state_authority"]

    _assert_no_authority(wrong_phase_packet)

    assert wrong_phase_packet["status"] == "blocked"
    assert wrong_phase_packet["state_passed"] is False
    assert "state_runtime_validation_failed" in wrong_phase_packet["errors"]

    summary_response = client.post(
        "/contractor-builder/state-authority/summary",
        json=_state_request(),
    )
    assert summary_response.status_code == 200, summary_response.text

    summary_payload = summary_response.json()
    assert summary_payload["status"] == "ok"
    assert summary_payload["mode"] == "read_only"
    assert summary_payload["execution_allowed"] is False
    assert summary_payload["mutation_allowed"] is False
    assert summary_payload["summary"]["state_passed"] is True

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "paths": paths,
        "direct_state_authority": {
            "status": direct_packet["status"],
            "state_passed": direct_packet["state_passed"],
            "authority_valid": direct_packet["validation"]["valid"],
        },
        "api_check": {
            "status": check_payload["status"],
            "state_status": api_packet["status"],
            "state_passed": api_packet["state_passed"],
        },
        "api_wrong_phase": {
            "state_status": wrong_phase_packet["status"],
            "state_passed": wrong_phase_packet["state_passed"],
            "errors": wrong_phase_packet["errors"],
        },
        "api_summary": {
            "status": summary_payload["status"],
            "state_passed": summary_payload["summary"]["state_passed"],
        },
        "health_route": {
            "state_authority": health_payload["routes"]["state_authority"],
        },
        "authority_confirmed": "state_authority_visible_read_only_no_mutation",
        "next": {
            "phase": "5E.4",
            "recommended_step": "Full State Authority regression across direct packet, Request Governor, API visibility, and health route.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5E3_STATE_AUTHORITY_VISIBILITY_PROBE: PASS")
    print(result)
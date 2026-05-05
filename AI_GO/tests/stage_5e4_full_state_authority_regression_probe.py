from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient

from AI_GO.app import app
from AI_GO.core.governance.request_governor import govern_request_from_dict
from AI_GO.core.state_runtime.state_authority import (
    build_state_authority_packet,
    summarize_state_authority,
)


PHASE = "5E.4"
PROBE_ID = "stage_5e4_full_state_authority_regression_probe"

PROJECT_ID = "project-stage_5e4_full_state_authority_regression_probe"
PHASE_ID = "phase-stage_5e4_closeout"


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
            "project_name": "Stage 5E.4 Full State Authority Regression Probe",
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


def _good_watcher() -> Dict[str, Any]:
    return {
        "status": "passed",
        "valid": True,
        "errors": [],
        "source": "stage_5e4_probe",
    }


def _checklist_summary(
    *,
    phase_id: str = PHASE_ID,
    ready: bool = True,
) -> Dict[str, Any]:
    return {
        "required_item_count": 1,
        "completed_required_count": 1 if ready else 0,
        "ready_for_signoff": ready,
        "phase_id": phase_id,
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


def _governor_request(
    *,
    project_id: str = PROJECT_ID,
    phase_id: str = PHASE_ID,
    operator_approved: bool = True,
    checklist_ready: bool = True,
) -> Dict[str, Any]:
    checklist_summary = _checklist_summary(
        phase_id=phase_id,
        ready=checklist_ready,
    )

    return {
        "request_id": f"stage-5e4-{project_id}-{phase_id}",
        "route": "/contractor-builder/phase-closeout/run",
        "method": "POST",
        "actor": "stage_5e4_probe",
        "target": "contractor_builder_v1.phase_closeout",
        "child_core_id": "contractor_builder_v1",
        "action_type": "phase_closeout",
        "action_class": "workflow_transition",
        "project_id": project_id,
        "phase_id": phase_id,
        "payload": {
            "receipt_planned": True,
            "state_mutation_declared": True,
            "operator_approved": operator_approved,
            "checklist_summary": checklist_summary,
        },
        "context": {
            "receipt_planned": True,
            "state_mutation_declared": True,
            "operator_approved": operator_approved,
            "watcher_result": _good_watcher(),
            "checklist_summary": checklist_summary,
        },
    }


def _read_request() -> Dict[str, Any]:
    return {
        "request_id": "stage-5e4-read",
        "route": "/contractor-builder/system-brain/summary",
        "method": "GET",
        "actor": "stage_5e4_probe",
        "target": "contractor_builder_v1.system_brain",
        "child_core_id": "contractor_builder_v1",
        "action_type": "read_dashboard",
        "action_class": "read",
        "project_id": "",
        "phase_id": "",
        "payload": {},
        "context": {},
    }


def _assert_no_authority(packet: Dict[str, Any]) -> None:
    authority = packet.get("authority", {})
    use_policy = packet.get("use_policy", {})

    assert isinstance(authority, dict)
    assert isinstance(use_policy, dict)

    for key in FORBIDDEN_AUTHORITY_TRUE:
        assert authority.get(key) is False, f"authority.{key} must remain false"

    for key in FORBIDDEN_USE_TRUE:
        assert use_policy.get(key) is False, f"use_policy.{key} must remain false"

    validation = packet.get("validation", {})
    assert validation.get("valid") is True
    assert validation.get("authority_violations") == []


def _assert_state_packet_passed(packet: Dict[str, Any]) -> None:
    assert packet["artifact_type"] == "state_authority_packet"
    assert packet["sealed"] is True
    assert packet["status"] == "passed", packet
    assert packet["allowed"] is True
    assert packet["valid"] is True
    assert packet["state_required"] is True
    assert packet["state_passed"] is True
    assert packet["state_validation"]["status"] == "passed"
    _assert_no_authority(packet)


def _assert_state_packet_blocked(packet: Dict[str, Any]) -> None:
    assert packet["artifact_type"] == "state_authority_packet"
    assert packet["sealed"] is True
    assert packet["status"] == "blocked", packet
    assert packet["allowed"] is False
    assert packet["valid"] is False
    assert packet["state_required"] is True
    assert packet["state_passed"] is False
    assert "state_runtime_validation_failed" in packet["errors"]
    _assert_no_authority(packet)


def _assert_governor_allowed(decision: Dict[str, Any]) -> None:
    assert decision["status"] == "passed", decision
    assert decision["allowed"] is True
    assert decision["valid"] is True
    assert decision["stages"]["state"]["status"] == "passed"
    assert decision["stages"]["state"]["allowed"] is True
    assert decision["stages"]["canon"]["status"] == "passed"
    assert decision["stages"]["canon"]["allowed"] is True
    assert decision["message"] == "Request passed State Authority and Canon Enforcer."


def _assert_governor_state_blocked(decision: Dict[str, Any]) -> None:
    assert decision["status"] == "blocked", decision
    assert decision["allowed"] is False
    assert decision["valid"] is False
    assert decision["stages"]["state"]["status"] == "blocked"
    assert decision["stages"]["canon"]["status"] == "not_run"
    assert decision["rejection_reasons"][0]["code"] == "state_authority_blocked"


def _assert_governor_canon_blocked(decision: Dict[str, Any]) -> None:
    assert decision["status"] == "blocked", decision
    assert decision["allowed"] is False
    assert decision["valid"] is False
    assert decision["stages"]["state"]["status"] == "passed"
    assert decision["stages"]["canon"]["status"] == "blocked"
    assert decision["rejection_reasons"][0]["code"] == "canon_enforcement_blocked"


def _assert_api_check_ok(payload: Dict[str, Any]) -> None:
    assert payload["status"] == "ok"
    assert payload["mode"] == "read_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert "state_authority" in payload
    assert "summary" in payload


def run_probe() -> Dict[str, Any]:
    paths = _prepare_project_state()

    direct_pass = build_state_authority_packet(_state_request())
    direct_wrong_phase = build_state_authority_packet(
        _state_request(phase_id="phase-not-current")
    )

    _assert_state_packet_passed(direct_pass)
    _assert_state_packet_blocked(direct_wrong_phase)

    direct_summary = summarize_state_authority(direct_pass)
    assert direct_summary["state_passed"] is True
    assert direct_summary["execution_allowed"] is False
    assert direct_summary["mutation_allowed"] is False

    governor_allowed = govern_request_from_dict(_governor_request())
    governor_wrong_phase = govern_request_from_dict(
        _governor_request(phase_id="phase-not-current")
    )
    governor_missing_project = govern_request_from_dict(
        _governor_request(project_id="", phase_id=PHASE_ID)
    )
    governor_missing_operator = govern_request_from_dict(
        _governor_request(operator_approved=False)
    )
    governor_checklist_not_ready = govern_request_from_dict(
        _governor_request(checklist_ready=False)
    )
    governor_read_only = govern_request_from_dict(_read_request())

    _assert_governor_allowed(governor_allowed)
    _assert_governor_state_blocked(governor_wrong_phase)
    _assert_governor_state_blocked(governor_missing_project)
    _assert_governor_canon_blocked(governor_missing_operator)
    _assert_governor_canon_blocked(governor_checklist_not_ready)

    assert governor_read_only["status"] == "passed"
    assert governor_read_only["allowed"] is True
    assert governor_read_only["stages"]["state"]["status"] == "passed"
    assert governor_read_only["stages"]["state"]["decision"]["state_required"] is False
    assert governor_read_only["stages"]["canon"]["status"] == "passed"

    client = TestClient(app)

    health_response = client.get("/contractor-builder/health")
    assert health_response.status_code == 200, health_response.text
    health_payload = health_response.json()
    assert health_payload["routes"]["state_authority"] is True
    assert health_payload["execution_allowed"] is False
    assert health_payload["approval_required"] is True

    api_check_response = client.post(
        "/contractor-builder/state-authority/check",
        json=_state_request(),
    )
    assert api_check_response.status_code == 200, api_check_response.text
    api_check_payload = api_check_response.json()
    _assert_api_check_ok(api_check_payload)
    _assert_state_packet_passed(api_check_payload["state_authority"])

    api_wrong_phase_response = client.post(
        "/contractor-builder/state-authority/check",
        json=_state_request(phase_id="phase-not-current"),
    )
    assert api_wrong_phase_response.status_code == 200, api_wrong_phase_response.text
    api_wrong_phase_payload = api_wrong_phase_response.json()
    _assert_api_check_ok(api_wrong_phase_payload)
    _assert_state_packet_blocked(api_wrong_phase_payload["state_authority"])

    api_summary_response = client.post(
        "/contractor-builder/state-authority/summary",
        json=_state_request(),
    )
    assert api_summary_response.status_code == 200, api_summary_response.text
    api_summary_payload = api_summary_response.json()
    assert api_summary_payload["status"] == "ok"
    assert api_summary_payload["mode"] == "read_only"
    assert api_summary_payload["execution_allowed"] is False
    assert api_summary_payload["mutation_allowed"] is False
    assert api_summary_payload["summary"]["state_passed"] is True

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "paths": paths,
        "direct_state_authority": {
            "passed_status": direct_pass["status"],
            "wrong_phase_status": direct_wrong_phase["status"],
            "summary_state_passed": direct_summary["state_passed"],
        },
        "request_governor": {
            "allowed": governor_allowed["status"],
            "wrong_phase": governor_wrong_phase["status"],
            "missing_project": governor_missing_project["status"],
            "missing_operator": governor_missing_operator["status"],
            "checklist_not_ready": governor_checklist_not_ready["status"],
            "read_only": governor_read_only["status"],
        },
        "api_visibility": {
            "health_state_authority": health_payload["routes"]["state_authority"],
            "check_status": api_check_payload["state_authority"]["status"],
            "wrong_phase_status": api_wrong_phase_payload["state_authority"]["status"],
            "summary_state_passed": api_summary_payload["summary"]["state_passed"],
        },
        "authority_confirmed": {
            "state_authority": "verification_only",
            "request_governor": "state_before_canon",
            "api": "read_only_visibility",
            "execution_allowed": False,
            "mutation_allowed": False,
        },
        "next": {
            "phase": "5E complete",
            "recommended_step": "Update Northstar handoff, then proceed to 5F External Memory integration when ready.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5E4_FULL_STATE_AUTHORITY_REGRESSION_PROBE: PASS")
    print(result)
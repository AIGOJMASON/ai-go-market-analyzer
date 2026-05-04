from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.request_governor import govern_request_from_dict


PHASE = "5E.2"
PROBE_ID = "stage_5e2_request_governor_state_authority_probe"

PROJECT_ID = "project-stage_5e2_request_governor_state_authority_probe"
PHASE_ID = "phase-stage_5e2_closeout"


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
            "project_name": "Stage 5E.2 Request Governor State Authority Probe",
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
        "source": "stage_5e2_probe",
    }


def _base_request(
    *,
    project_id: str = PROJECT_ID,
    phase_id: str = PHASE_ID,
    operator_approved: bool = True,
    watcher_result: Dict[str, Any] | None = None,
    checklist_ready: bool = True,
) -> Dict[str, Any]:
    checklist_summary = {
        "required_item_count": 1,
        "completed_required_count": 1 if checklist_ready else 0,
        "ready_for_signoff": checklist_ready,
        "phase_id": phase_id,
    }

    return {
        "request_id": f"stage-5e2-{project_id}-{phase_id}",
        "route": "/contractor-builder/phase-closeout/run",
        "method": "POST",
        "actor": "stage_5e2_probe",
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
            "watcher_result": watcher_result or _good_watcher(),
            "checklist_summary": checklist_summary,
        },
    }


def _read_request() -> Dict[str, Any]:
    return {
        "request_id": "stage-5e2-read",
        "route": "/contractor-builder/system-brain/summary",
        "method": "GET",
        "actor": "stage_5e2_probe",
        "target": "contractor_builder_v1.system_brain",
        "child_core_id": "contractor_builder_v1",
        "action_type": "read_dashboard",
        "action_class": "read",
        "project_id": "",
        "phase_id": "",
        "payload": {},
        "context": {},
    }


def run_probe() -> Dict[str, Any]:
    paths = _prepare_project_state()

    allowed = govern_request_from_dict(_base_request())

    wrong_phase = govern_request_from_dict(
        _base_request(phase_id="phase-not-current")
    )

    missing_project = govern_request_from_dict(
        _base_request(project_id="", phase_id=PHASE_ID)
    )

    missing_operator = govern_request_from_dict(
        _base_request(operator_approved=False)
    )

    checklist_not_ready = govern_request_from_dict(
        _base_request(checklist_ready=False)
    )

    read_only = govern_request_from_dict(_read_request())

    assert allowed["status"] == "passed", allowed
    assert allowed["allowed"] is True
    assert allowed["stages"]["state"]["status"] == "passed"
    assert allowed["stages"]["state"]["allowed"] is True
    assert allowed["stages"]["state"]["decision"]["state_passed"] is True
    assert allowed["stages"]["canon"]["status"] == "passed"
    assert allowed["stages"]["canon"]["allowed"] is True

    canon_context = allowed["stages"]["canon"]["decision"]["action"]
    assert canon_context["phase_id"] == PHASE_ID

    assert wrong_phase["status"] == "blocked"
    assert wrong_phase["allowed"] is False
    assert wrong_phase["stages"]["state"]["status"] == "blocked"
    assert wrong_phase["stages"]["canon"]["status"] == "not_run"
    assert wrong_phase["rejection_reasons"][0]["code"] == "state_authority_blocked"

    assert missing_project["status"] == "blocked"
    assert missing_project["allowed"] is False
    assert missing_project["stages"]["state"]["status"] == "blocked"
    assert missing_project["stages"]["canon"]["status"] == "not_run"

    assert missing_operator["status"] == "blocked"
    assert missing_operator["allowed"] is False
    assert missing_operator["stages"]["state"]["status"] == "passed"
    assert missing_operator["stages"]["canon"]["status"] == "blocked"
    assert missing_operator["rejection_reasons"][0]["code"] == "canon_enforcement_blocked"

    assert checklist_not_ready["status"] == "blocked"
    assert checklist_not_ready["allowed"] is False
    assert checklist_not_ready["stages"]["state"]["status"] == "passed"
    assert checklist_not_ready["stages"]["canon"]["status"] == "blocked"
    assert checklist_not_ready["rejection_reasons"][0]["code"] == "canon_enforcement_blocked"

    assert read_only["status"] == "passed"
    assert read_only["allowed"] is True
    assert read_only["stages"]["state"]["status"] == "passed"
    assert read_only["stages"]["state"]["decision"]["state_required"] is False
    assert read_only["stages"]["canon"]["status"] == "passed"

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "paths": paths,
        "allowed_case": {
            "request_status": allowed["status"],
            "state_status": allowed["stages"]["state"]["status"],
            "canon_status": allowed["stages"]["canon"]["status"],
        },
        "wrong_phase_case": {
            "request_status": wrong_phase["status"],
            "state_status": wrong_phase["stages"]["state"]["status"],
            "canon_status": wrong_phase["stages"]["canon"]["status"],
        },
        "missing_project_case": {
            "request_status": missing_project["status"],
            "state_status": missing_project["stages"]["state"]["status"],
            "canon_status": missing_project["stages"]["canon"]["status"],
        },
        "missing_operator_case": {
            "request_status": missing_operator["status"],
            "state_status": missing_operator["stages"]["state"]["status"],
            "canon_status": missing_operator["stages"]["canon"]["status"],
        },
        "checklist_not_ready_case": {
            "request_status": checklist_not_ready["status"],
            "state_status": checklist_not_ready["stages"]["state"]["status"],
            "canon_status": checklist_not_ready["stages"]["canon"]["status"],
        },
        "read_only_case": {
            "request_status": read_only["status"],
            "state_required": read_only["stages"]["state"]["decision"]["state_required"],
            "canon_status": read_only["stages"]["canon"]["status"],
        },
        "authority_confirmed": "request_governor_state_stage_supplies_truth_context_before_canon",
        "next": {
            "phase": "5E.3",
            "recommended_step": "Add State Authority API/surface visibility and root-stage regression.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5E2_REQUEST_GOVERNOR_STATE_AUTHORITY_PROBE: PASS")
    print(result)
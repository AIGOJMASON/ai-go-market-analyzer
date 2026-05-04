from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.state_runtime.state_authority import (
    build_state_authority_packet,
    summarize_state_authority,
)


PHASE = "5E.1"
PROBE_ID = "stage_5e1_state_authority_probe"


PROJECT_ID = "project-stage_5e1_state_authority_probe"
PHASE_ID = "phase-stage_5e1_closeout"


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


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
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
            "project_name": "Stage 5E.1 State Authority Probe",
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


def _assert_no_authority(packet: Dict[str, Any]) -> None:
    authority = packet.get("authority", {})
    use_policy = packet.get("use_policy", {})

    assert authority["mode"] == "state_verification_only"
    assert authority["read_only"] is True
    assert authority["can_verify_state"] is True

    for key in FORBIDDEN_AUTHORITY_TRUE:
        assert authority.get(key) is False, f"authority.{key} must remain false"

    for key in FORBIDDEN_USE_TRUE:
        assert use_policy.get(key) is False, f"use_policy.{key} must remain false"

    validation = packet["validation"]
    assert validation["valid"] is True
    assert validation["authority_violations"] == []


def _build_allowed_case() -> Dict[str, Any]:
    return build_state_authority_packet(
        {
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": PROJECT_ID,
            "phase_id": PHASE_ID,
            "payload": {},
            "context": {},
        }
    )


def _build_missing_project_case() -> Dict[str, Any]:
    return build_state_authority_packet(
        {
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": "",
            "phase_id": PHASE_ID,
            "payload": {},
            "context": {},
        }
    )


def _build_wrong_phase_case() -> Dict[str, Any]:
    return build_state_authority_packet(
        {
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": PROJECT_ID,
            "phase_id": "phase-not-current",
            "payload": {},
            "context": {},
        }
    )


def _build_read_case() -> Dict[str, Any]:
    return build_state_authority_packet(
        {
            "action_type": "read_dashboard",
            "action_class": "read",
            "project_id": "",
            "phase_id": "",
            "payload": {},
            "context": {},
        }
    )


def run_probe() -> Dict[str, Any]:
    paths = _prepare_project_state()

    allowed_case = _build_allowed_case()
    missing_project_case = _build_missing_project_case()
    wrong_phase_case = _build_wrong_phase_case()
    read_case = _build_read_case()

    _assert_no_authority(allowed_case)
    _assert_no_authority(missing_project_case)
    _assert_no_authority(wrong_phase_case)
    _assert_no_authority(read_case)

    assert allowed_case["status"] == "passed", allowed_case
    assert allowed_case["valid"] is True
    assert allowed_case["allowed"] is True
    assert allowed_case["state_required"] is True
    assert allowed_case["state_passed"] is True
    assert allowed_case["state_validation"]["valid"] is True

    assert missing_project_case["status"] == "blocked"
    assert missing_project_case["allowed"] is False
    assert "state_required_project_id_missing" in missing_project_case["errors"]

    assert wrong_phase_case["status"] == "blocked"
    assert wrong_phase_case["allowed"] is False
    assert "state_runtime_validation_failed" in wrong_phase_case["errors"]

    assert read_case["status"] == "passed"
    assert read_case["state_required"] is False
    assert read_case["state_passed"] is True
    assert "state_validation_not_required_for_action" in read_case["warnings"]

    summary = summarize_state_authority(allowed_case)
    assert summary["state_passed"] is True
    assert summary["execution_allowed"] is False
    assert summary["mutation_allowed"] is False

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "paths": paths,
        "allowed_case": {
            "status": allowed_case["status"],
            "state_passed": allowed_case["state_passed"],
            "state_validation_status": allowed_case["state_validation"]["status"],
        },
        "missing_project_case": {
            "status": missing_project_case["status"],
            "errors": missing_project_case["errors"],
        },
        "wrong_phase_case": {
            "status": wrong_phase_case["status"],
            "errors": wrong_phase_case["errors"],
        },
        "read_case": {
            "status": read_case["status"],
            "state_required": read_case["state_required"],
            "warnings": read_case["warnings"],
        },
        "summary_contract": summary,
        "authority_confirmed": "state_verification_only_no_execution_no_mutation",
        "next": {
            "phase": "5E.2",
            "recommended_step": "Wire State Authority into Request Governor as the real state stage before canon pass for mutating actions.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5E1_STATE_AUTHORITY_PROBE: PASS")
    print(result)
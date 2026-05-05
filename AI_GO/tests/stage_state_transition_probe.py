from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.canon_runtime.canon_enforcer import enforce_canon_action_from_dict


PROBE_NAME = "STAGE_STATE_TRANSITION_PROBE"


def _reason_codes(decision: Dict[str, Any]) -> List[str]:
    return [
        str(reason.get("code"))
        for reason in decision.get("rejection_reasons", [])
        if isinstance(reason, dict)
    ]


def _base_action() -> Dict[str, Any]:
    return {
        "action_type": "send_phase_closeout",
        "action_class": "workflow_transition",
        "actor": "stage_state_transition_probe",
        "target": "contractor_builder_v1.phase_closeout",
        "project_id": "project-state-transition-probe",
        "phase_id": "phase-state-transition-current",
        "route": "/contractor-builder/phase-closeout/run",
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
            "workflow_state": {
                "project_id": "project-state-transition-probe",
                "current_phase_id": "phase-state-transition-current",
                "workflow_status": "active",
            },
            "phase_instance": {
                "phase_id": "phase-state-transition-current",
                "phase_status": "awaiting_signoff",
            },
            "checklist_summary": {
                "ready_for_signoff": True,
                "required_item_count": 2,
                "completed_required_count": 2,
            },
        },
    }


def _case_valid_closeout_allowed() -> Dict[str, Any]:
    action = _base_action()
    decision = enforce_canon_action_from_dict(action)

    passed = decision.get("allowed") is True

    return {
        "case": "valid_closeout_allowed",
        "expected": "allowed",
        "passed": passed,
        "decision_status": decision.get("status"),
        "decision_allowed": decision.get("allowed"),
        "reason_codes": _reason_codes(decision),
    }


def _case_blocks_checklist_not_ready() -> Dict[str, Any]:
    action = _base_action()
    action["context"]["checklist_summary"]["ready_for_signoff"] = False
    action["context"]["checklist_summary"]["completed_required_count"] = 1

    decision = enforce_canon_action_from_dict(action)
    codes = set(_reason_codes(decision))

    passed = (
        decision.get("allowed") is False
        and "checklist_not_ready" in codes
    )

    return {
        "case": "blocks_checklist_not_ready",
        "expected": "blocked",
        "passed": passed,
        "decision_status": decision.get("status"),
        "decision_allowed": decision.get("allowed"),
        "reason_codes": sorted(codes),
    }


def _case_blocks_phase_not_awaiting_signoff() -> Dict[str, Any]:
    action = _base_action()
    action["context"]["phase_instance"]["phase_status"] = "active"

    decision = enforce_canon_action_from_dict(action)
    codes = set(_reason_codes(decision))

    passed = (
        decision.get("allowed") is False
        and "phase_not_awaiting_signoff" in codes
    )

    return {
        "case": "blocks_phase_not_awaiting_signoff",
        "expected": "blocked",
        "passed": passed,
        "decision_status": decision.get("status"),
        "decision_allowed": decision.get("allowed"),
        "reason_codes": sorted(codes),
    }


def _case_blocks_phase_not_current() -> Dict[str, Any]:
    action = _base_action()
    action["context"]["workflow_state"]["current_phase_id"] = "phase-state-transition-other"

    decision = enforce_canon_action_from_dict(action)
    codes = set(_reason_codes(decision))

    passed = (
        decision.get("allowed") is False
        and "phase_not_current" in codes
    )

    return {
        "case": "blocks_phase_not_current",
        "expected": "blocked",
        "passed": passed,
        "decision_status": decision.get("status"),
        "decision_allowed": decision.get("allowed"),
        "reason_codes": sorted(codes),
    }


def run_probe() -> Dict[str, Any]:
    results = [
        _case_valid_closeout_allowed(),
        _case_blocks_checklist_not_ready(),
        _case_blocks_phase_not_awaiting_signoff(),
        _case_blocks_phase_not_current(),
    ]

    failed = [item for item in results if item.get("passed") is not True]

    return {
        "probe": PROBE_NAME,
        "status": "passed" if not failed else "failed",
        "failed_count": len(failed),
        "failed": failed,
        "results": results,
        "mutation_allowed": False,
        "writes_performed": False,
    }


if __name__ == "__main__":
    output = run_probe()
    print(f"{PROBE_NAME}: {output['status'].upper()}")
    print("\nOUTPUT:\n", output)
from __future__ import annotations

import copy
import json

from AI_GO.core.watcher.watcher_enforcement import (
    assert_watcher_allowed,
    enforce_watcher_decision,
)


def _base_payload() -> dict:
    return {
        "state": {
            "valid": True,
            "status": "passed",
        },
        "watcher": {
            "valid": True,
            "status": "passed",
        },
        "execution_gate": {
            "allowed": True,
            "status": "allowed",
        },
        "result_summary": {
            "artifact_type": "post_execution_result_summary",
            "artifact_version": "v1",
            "created_at": "2026-04-29T23:46:57.941775+00:00",
            "action": "decision_create",
            "status": "created",
            "effect": "execution_completed",
            "project_id": "project-watcher-enforcement-probe",
            "phase_id": "",
            "artifacts_created": [],
            "external_actions": [],
            "state_mutations": [],
            "counts": {
                "artifacts_created": 0,
                "external_actions": 0,
                "state_mutations": 0,
            },
            "sealed": True,
        },
        "pm_behavior_application": {
            "artifact_type": "contractor_pm_controlled_behavior_application",
            "artifact_version": "v1.0",
            "application_id": "pm_behavior_probe",
            "target_service": "decision",
            "usable_refinement_count": 1,
            "blocked_refinement_count": 0,
            "behavior_items": [
                {
                    "target_service": "decision",
                    "behavior_class": "decision_annotation_guidance",
                    "advisory_flags": [
                        "requires_pm_caution_note",
                        "unverified_assumption_present",
                    ],
                    "suggested_note_fragments": [
                        "Decision should preserve PM refinement lineage."
                    ],
                    "may_block": False,
                    "may_mutate": False,
                    "may_execute": False,
                }
            ],
            "authority": {
                "pm_owned": True,
                "advisory_only": True,
                "execution_allowed": False,
                "mutation_allowed": False,
                "grants_authority": False,
                "downstream_service_must_revalidate": True,
                "downstream_governance_required": True,
            },
            "constraints": {
                "no_direct_state_mutation": True,
                "no_direct_external_action": True,
                "no_auto_blocking": True,
                "no_auto_execution": True,
                "annotation_only": True,
            },
            "sealed": True,
        },
    }


def run_probe() -> dict:
    allowed_payload = _base_payload()

    allowed_decision = enforce_watcher_decision(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_watcher_enforcement_probe",
    )

    assert allowed_decision["artifact_type"] == "watcher_enforcement_decision"
    assert allowed_decision["allowed"] is True
    assert allowed_decision["blocked"] is False
    assert allowed_decision["status"] == "allowed_with_escalation"
    assert allowed_decision["decision"] == "allow_with_escalation"
    assert allowed_decision["escalation_required"] is True
    assert allowed_decision["rollback_recommended"] is False
    assert allowed_decision["authority"]["may_block"] is True
    assert allowed_decision["authority"]["may_execute_rollback"] is False
    assert allowed_decision["constraints"]["decision_only"] is True
    assert allowed_decision["sealed"] is True

    assert_watcher_allowed(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_watcher_enforcement_probe",
    )

    blocked_payload = copy.deepcopy(allowed_payload)
    blocked_payload["watcher"] = {
        "valid": False,
        "status": "failed",
        "errors": ["simulated_watcher_failure"],
    }

    blocked_decision = enforce_watcher_decision(
        payload=blocked_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_watcher_enforcement_probe",
    )

    assert blocked_decision["allowed"] is False
    assert blocked_decision["blocked"] is True
    assert blocked_decision["status"] == "blocked"
    assert blocked_decision["decision"] == "block"
    assert blocked_decision["rollback_recommended"] is True

    blocked_codes = {reason["code"] for reason in blocked_decision["reasons"]}
    assert "watcher_invalid" in blocked_codes

    authority_violation_payload = copy.deepcopy(allowed_payload)
    authority_violation_payload["pm_behavior_application"]["behavior_items"][0][
        "may_execute"
    ] = True

    authority_violation_decision = enforce_watcher_decision(
        payload=authority_violation_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_watcher_enforcement_probe",
    )

    assert authority_violation_decision["allowed"] is False
    assert authority_violation_decision["blocked"] is True
    authority_codes = {
        reason["code"] for reason in authority_violation_decision["reasons"]
    }
    assert "pm_behavior_authority_violation" in authority_codes

    return {
        "status": "passed",
        "phase": "3.1",
        "link": "watcher_enforcement_decision",
        "allowed_decision": allowed_decision,
        "blocked_decision": blocked_decision,
        "authority_violation_decision": authority_violation_decision,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_WATCHER_ENFORCEMENT_PROBE: PASS")
    print(json.dumps(output, indent=2))
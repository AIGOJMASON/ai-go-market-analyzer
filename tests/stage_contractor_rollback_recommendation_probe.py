from __future__ import annotations

import copy
import json

from AI_GO.core.watcher.rollback_recommendation import (
    build_rollback_recommendation,
)
from AI_GO.core.watcher.watcher_enforcement import (
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
            "project_id": "project-rollback-recommendation-probe",
            "phase_id": "",
            "artifacts_created": [
                {
                    "artifact_type": "contractor_decision_receipt",
                    "path": "AI_GO/receipts/contractor_builder_v1/decision_log/receipt-probe.json",
                }
            ],
            "external_actions": [],
            "state_mutations": [
                {
                    "artifact_type": "contractor_decision_record",
                    "path": "AI_GO/state/contractor_builder_v1/projects/by_project/project-rollback-recommendation-probe/decision_log/decisions.jsonl",
                }
            ],
            "counts": {
                "artifacts_created": 1,
                "external_actions": 0,
                "state_mutations": 1,
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

    allowed_watcher_decision = enforce_watcher_decision(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    allowed_payload["watcher_enforcement_decision"] = allowed_watcher_decision

    allowed_recommendation = build_rollback_recommendation(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    assert allowed_recommendation["artifact_type"] == "watcher_rollback_recommendation"
    assert allowed_recommendation["recommendation_class"] == "escalation_review_only"
    assert allowed_recommendation["severity"] == "medium"
    assert allowed_recommendation["rollback_execution_allowed"] is False
    assert allowed_recommendation["state_mutation_allowed"] is False
    assert allowed_recommendation["external_action_allowed"] is False
    assert allowed_recommendation["authority"]["recommendation_only"] is True
    assert allowed_recommendation["authority"]["may_execute_rollback"] is False
    assert allowed_recommendation["constraints"]["no_direct_state_mutation"] is True
    assert allowed_recommendation["sealed"] is True

    blocked_payload = copy.deepcopy(allowed_payload)
    blocked_payload["watcher"] = {
        "valid": False,
        "status": "failed",
        "errors": ["simulated_watcher_failure"],
    }

    blocked_watcher_decision = enforce_watcher_decision(
        payload=blocked_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    blocked_payload["watcher_enforcement_decision"] = blocked_watcher_decision

    blocked_recommendation = build_rollback_recommendation(
        payload=blocked_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    assert blocked_recommendation["recommendation_class"] == "rollback_review_required"
    assert blocked_recommendation["severity"] == "high"
    assert blocked_recommendation["authority"]["operator_required"] is True
    assert blocked_recommendation["rollback_execution_allowed"] is False
    assert blocked_recommendation["affected_artifacts"]["state_mutations"]
    assert blocked_recommendation["affected_artifacts"]["artifacts_created"]

    blocked_reason_codes = {
        reason["code"] for reason in blocked_recommendation["reasons"]
    }
    assert "watcher_invalid" in blocked_reason_codes

    review_steps = {
        step["step"] for step in blocked_recommendation["recommended_steps"]
    }
    assert "freeze_follow_on_actions" in review_steps
    assert "review_state_mutations" in review_steps
    assert "review_created_artifacts" in review_steps
    assert "operator_decision_required" in review_steps

    no_rollback_payload = _base_payload()
    no_rollback_payload["pm_behavior_application"] = {}

    no_rollback_watcher_decision = enforce_watcher_decision(
        payload=no_rollback_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    no_rollback_payload["watcher_enforcement_decision"] = no_rollback_watcher_decision

    no_rollback_recommendation = build_rollback_recommendation(
        payload=no_rollback_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_rollback_recommendation_probe",
    )

    assert no_rollback_recommendation["recommendation_class"] == "no_rollback_recommended"
    assert no_rollback_recommendation["severity"] == "low"
    assert no_rollback_recommendation["authority"]["operator_required"] is False

    return {
        "status": "passed",
        "phase": "3.2",
        "link": "rollback_recommendation",
        "allowed_recommendation": allowed_recommendation,
        "blocked_recommendation": blocked_recommendation,
        "no_rollback_recommendation": no_rollback_recommendation,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_ROLLBACK_RECOMMENDATION_PROBE: PASS")
    print(json.dumps(output, indent=2))
from __future__ import annotations

import copy
import json

from AI_GO.core.watcher.escalation_routing import build_escalation_route
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
            "project_id": "project-escalation-routing-probe",
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
                    "path": "AI_GO/state/contractor_builder_v1/projects/by_project/project-escalation-routing-probe/decision_log/decisions.jsonl",
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


def _build_route_bundle(payload: dict) -> dict:
    watcher_decision = enforce_watcher_decision(
        payload=payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_escalation_routing_probe",
    )

    enriched = copy.deepcopy(payload)
    enriched["watcher_enforcement_decision"] = watcher_decision

    rollback_recommendation = build_rollback_recommendation(
        payload=enriched,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_escalation_routing_probe",
    )

    enriched["rollback_recommendation"] = rollback_recommendation

    escalation_route = build_escalation_route(
        payload=enriched,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_escalation_routing_probe",
    )

    return {
        "watcher_decision": watcher_decision,
        "rollback_recommendation": rollback_recommendation,
        "escalation_route": escalation_route,
    }


def run_probe() -> dict:
    caution_payload = _base_payload()
    caution_bundle = _build_route_bundle(caution_payload)
    caution_route = caution_bundle["escalation_route"]

    assert caution_route["artifact_type"] == "watcher_escalation_route"
    assert caution_route["route_class"] == "caution_review"
    assert caution_route["severity"] == "medium"
    assert caution_route["routing_actions"]["pm_review_required"] is True
    assert caution_route["routing_actions"]["operator_review_required"] is False
    assert caution_route["routing_actions"]["external_notification_allowed"] is False
    assert caution_route["authority"]["routing_only"] is True
    assert caution_route["authority"]["may_notify_external"] is False
    assert caution_route["authority"]["may_mutate_state"] is False
    assert caution_route["authority"]["may_execute"] is False
    assert caution_route["constraints"]["no_direct_notification"] is True
    assert caution_route["sealed"] is True
    assert "pm_behavior_caution_escalation" in caution_route["reason_codes"]

    blocked_payload = _base_payload()
    blocked_payload["watcher"] = {
        "valid": False,
        "status": "failed",
        "errors": ["simulated_watcher_failure"],
    }

    blocked_bundle = _build_route_bundle(blocked_payload)
    blocked_route = blocked_bundle["escalation_route"]

    assert blocked_route["route_class"] == "rollback_review"
    assert blocked_route["severity"] == "high"
    assert blocked_route["routing_actions"]["operator_review_required"] is True
    assert blocked_route["routing_actions"]["pm_review_required"] is True
    assert blocked_route["authority"]["operator_required"] is True
    assert "watcher_invalid" in blocked_route["reason_codes"]
    assert blocked_route["affected_artifacts"]["state_mutations"]
    assert blocked_route["affected_artifacts"]["artifacts_created"]

    informational_payload = _base_payload()
    informational_payload["pm_behavior_application"] = {}

    informational_bundle = _build_route_bundle(informational_payload)
    informational_route = informational_bundle["escalation_route"]

    assert informational_route["route_class"] == "informational"
    assert informational_route["severity"] == "low"
    assert informational_route["routing_actions"]["pm_review_required"] is False
    assert informational_route["routing_actions"]["operator_review_required"] is False
    assert informational_route["authority"]["operator_required"] is False
    assert informational_route["reason_codes"] == []

    return {
        "status": "passed",
        "phase": "3.3",
        "link": "escalation_routing",
        "caution_route": caution_route,
        "blocked_route": blocked_route,
        "informational_route": informational_route,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_ESCALATION_ROUTING_PROBE: PASS")
    print(json.dumps(output, indent=2))
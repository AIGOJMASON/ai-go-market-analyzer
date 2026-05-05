from __future__ import annotations

import copy
import json

from AI_GO.core.watcher.pre_execution_hard_gate import (
    assert_pre_execution_allowed,
    evaluate_pre_execution_hard_gate,
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


def _with_watcher_enforcement(payload: dict) -> dict:
    enriched = copy.deepcopy(payload)

    watcher_enforcement_decision = enforce_watcher_decision(
        payload=enriched,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    enriched["watcher_enforcement_decision"] = watcher_enforcement_decision
    return enriched


def run_probe() -> dict:
    allowed_payload = _with_watcher_enforcement(_base_payload())

    allowed_gate = evaluate_pre_execution_hard_gate(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    assert allowed_gate["artifact_type"] == "pre_execution_hard_gate_decision"
    assert allowed_gate["allowed"] is True
    assert allowed_gate["blocked"] is False
    assert allowed_gate["status"] == "allowed_with_escalation"
    assert allowed_gate["decision"] == "allow_with_escalation"
    assert allowed_gate["escalation_required"] is True
    assert allowed_gate["authority"]["may_block_execution"] is True
    assert allowed_gate["authority"]["may_execute"] is False
    assert allowed_gate["constraints"]["must_precede_executor"] is True
    assert allowed_gate["constraints"]["missing_watcher_enforcement_blocks"] is True
    assert allowed_gate["sealed"] is True

    assert_pre_execution_allowed(
        payload=allowed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    missing_enforcement_payload = _base_payload()

    missing_gate = evaluate_pre_execution_hard_gate(
        payload=missing_enforcement_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    assert missing_gate["allowed"] is False
    assert missing_gate["blocked"] is True
    assert missing_gate["status"] == "blocked"
    missing_codes = {reason["code"] for reason in missing_gate["reasons"]}
    assert "watcher_enforcement_missing" in missing_codes

    blocked_payload = _base_payload()
    blocked_payload["watcher"] = {
        "valid": False,
        "status": "failed",
        "errors": ["simulated_watcher_failure"],
    }
    blocked_payload = _with_watcher_enforcement(blocked_payload)

    blocked_gate = evaluate_pre_execution_hard_gate(
        payload=blocked_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    assert blocked_gate["allowed"] is False
    assert blocked_gate["blocked"] is True
    blocked_codes = {reason["code"] for reason in blocked_gate["reasons"]}
    assert "base_watcher_invalid" in blocked_codes
    assert "watcher_enforcement_blocked" in blocked_codes

    malformed_payload = _with_watcher_enforcement(_base_payload())
    malformed_payload["watcher_enforcement_decision"] = {
        "artifact_type": "watcher_enforcement_decision",
        "status": "allowed",
        "decision": "allow",
        "allowed": True,
        "blocked": False,
        "sealed": False,
    }

    malformed_gate = evaluate_pre_execution_hard_gate(
        payload=malformed_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    assert malformed_gate["allowed"] is False
    assert malformed_gate["blocked"] is True
    malformed_codes = {reason["code"] for reason in malformed_gate["reasons"]}
    assert "watcher_enforcement_invalid_shape" in malformed_codes

    execution_gate_blocked_payload = _with_watcher_enforcement(_base_payload())
    execution_gate_blocked_payload["execution_gate"] = {
        "allowed": False,
        "status": "blocked",
        "reasons": ["simulated_execution_gate_block"],
    }

    execution_gate_blocked = evaluate_pre_execution_hard_gate(
        payload=execution_gate_blocked_payload,
        action="decision_create",
        profile="contractor_decision",
        actor="stage_contractor_pre_execution_hard_gate_probe",
    )

    assert execution_gate_blocked["allowed"] is False
    assert execution_gate_blocked["blocked"] is True
    gate_codes = {reason["code"] for reason in execution_gate_blocked["reasons"]}
    assert "execution_gate_not_allowed" in gate_codes

    return {
        "status": "passed",
        "phase": "3.4",
        "link": "pre_execution_hard_gate",
        "allowed_gate": allowed_gate,
        "missing_gate": missing_gate,
        "blocked_gate": blocked_gate,
        "malformed_gate": malformed_gate,
        "execution_gate_blocked": execution_gate_blocked,
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_PRE_EXECUTION_HARD_GATE_PROBE: PASS")
    print(json.dumps(output, indent=2))
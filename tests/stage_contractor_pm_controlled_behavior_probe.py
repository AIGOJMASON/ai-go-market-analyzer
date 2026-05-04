from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_service import (
    create_assumption,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_service import (
    create_decision,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.controlled_behavior_application import (
    apply_behavior_annotations_to_payload,
    build_behavior_application,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_context,
    extract_target_context,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_refinement_layer import (
    build_coupling_refinement_context,
)


def run_probe() -> dict:
    project_id = "project-pm-controlled-behavior-probe"
    phase_id = "phase-pm-controlled-behavior-probe"
    assumption_id = "assumption-pm-controlled-behavior-probe-001"
    decision_id = "decision-pm-controlled-behavior-probe-001"

    assumption_result = create_assumption(
        {
            "actor": "stage_contractor_pm_controlled_behavior_probe",
            "entry_kwargs": {
                "assumption_id": assumption_id,
                "project_id": project_id,
                "statement": (
                    "Cabinet delivery date is assumed stable but remains unverified."
                ),
                "source_type": "Other",
                "source_reference": "stage_contractor_pm_controlled_behavior_probe",
                "logged_by": "AI_GO",
                "owner_acknowledged": "Not_Required",
                "validation_status": "Unverified",
                "impact_if_false": (
                    "Decision language should remain cautious until delivery date is verified."
                ),
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],
                "linked_risk_ids": [],
                "notes": (
                    "Phase 2G.6 probe. Assumption should drive controlled behavior annotations."
                ),
            },
        }
    )

    assert assumption_result["mode"] == "governed_execution"
    assert assumption_result["status"] == "created"
    assert assumption_result["state"]["valid"] is True
    assert assumption_result["watcher"]["valid"] is True
    assert assumption_result["execution_gate"]["allowed"] is True
    assert assumption_result["result_summary"]["effect"] == "execution_completed"

    coupling_context = build_pm_coupling_context(
        project_id=project_id,
        phase_id=phase_id,
        assumption_records=[assumption_result],
        actor="PM_CORE",
    )

    decision_pm_context = extract_target_context(
        coupling_context=coupling_context,
        target_service="decision",
    )

    refinement_context = build_coupling_refinement_context(
        coupling_context=decision_pm_context,
        target_service="decision",
        actor="PM_CORE",
    )

    behavior_application = build_behavior_application(
        refinement_context=refinement_context,
        target_service="decision",
        actor="PM_CORE",
    )

    assert (
        behavior_application["artifact_type"]
        == "contractor_pm_controlled_behavior_application"
    )
    assert behavior_application["target_service"] == "decision"
    assert behavior_application["usable_refinement_count"] == 1
    assert behavior_application["blocked_refinement_count"] == 0
    assert behavior_application["authority"]["advisory_only"] is True
    assert behavior_application["authority"]["execution_allowed"] is False
    assert behavior_application["authority"]["mutation_allowed"] is False
    assert behavior_application["authority"]["grants_authority"] is False
    assert behavior_application["constraints"]["annotation_only"] is True
    assert behavior_application["constraints"]["no_auto_execution"] is True
    assert behavior_application["sealed"] is True

    behavior_item = behavior_application["behavior_items"][0]
    assert behavior_item["target_service"] == "decision"
    assert behavior_item["behavior_class"] == "decision_annotation_guidance"
    assert behavior_item["may_block"] is False
    assert behavior_item["may_mutate"] is False
    assert behavior_item["may_execute"] is False
    assert "unverified_assumption_present" in behavior_item["advisory_flags"]

    base_decision_payload = {
        "actor": "stage_contractor_pm_controlled_behavior_probe",
        "pm_context": decision_pm_context,
        "pm_refinement_context": refinement_context,
        "entry_kwargs": {
            "decision_id": decision_id,
            "project_id": project_id,
            "title": "PM Controlled Behavior Probe Decision",
            "decision_type": "Risk_Acceptance",
            "phase_id": phase_id,
            "expected_risk_level": "Moderate",
            "notes_on_assumptions": (
                "Decision receives controlled behavior annotations only."
            ),
            "may_reference_in_owner_reports": True,
            "owner_report_reference_label": "PM controlled behavior probe",
            "notes_internal": (
                "Phase 2G.6 baseline note before behavior application."
            ),
            "attachments_refs": [],
        },
    }

    decision_payload = apply_behavior_annotations_to_payload(
        payload=base_decision_payload,
        behavior_application=behavior_application,
        note_field="notes_internal",
    )

    assert "PM behavior guidance:" in decision_payload["entry_kwargs"]["notes_internal"]
    assert (
        "unverified_assumption_present"
        in decision_payload["entry_kwargs"]["notes_internal"]
    )
    assert "pm_behavior_application" in decision_payload

    assert "pm_behavior_flags" not in decision_payload["entry_kwargs"]
    assert "pm_behavior_application_id" not in decision_payload["entry_kwargs"]
    assert "pm_behavior_application_hash" not in decision_payload["entry_kwargs"]

    decision_result = create_decision(decision_payload)

    assert decision_result["mode"] == "governed_execution"
    assert decision_result["status"] == "created"
    assert decision_result["state"]["valid"] is True
    assert decision_result["watcher"]["valid"] is True
    assert decision_result["execution_gate"]["allowed"] is True
    assert decision_result["entry"]["decision_id"] == decision_id
    assert (
        decision_result["result_summary"]["artifact_type"]
        == "post_execution_result_summary"
    )
    assert decision_result["result_summary"]["effect"] == "execution_completed"

    return {
        "status": "passed",
        "phase": "2G.6",
        "link": "controlled_behavior_application",
        "assumption": {
            "assumption_id": assumption_result["entry"]["assumption_id"],
            "artifact_path": assumption_result["artifact_path"],
            "receipt_path": assumption_result["receipt_path"],
            "result_summary": assumption_result["result_summary"],
        },
        "coupling": {
            "context_hash": coupling_context["context_hash"],
            "decision_packet_count": decision_pm_context["packet_count"],
            "decision_packet": decision_pm_context["packets"][0],
        },
        "refinement": {
            "refinement_context_hash": refinement_context["refinement_context_hash"],
            "refinement_count": refinement_context["refinement_count"],
            "first_refinement": refinement_context["refinements"][0],
        },
        "behavior_application": behavior_application,
        "decision_downstream_validation": {
            "decision_id": decision_result["entry"]["decision_id"],
            "artifact_path": decision_result["artifact_path"],
            "receipt_path": decision_result["receipt_path"],
            "result_summary": decision_result["result_summary"],
        },
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_PM_CONTROLLED_BEHAVIOR_PROBE: PASS")
    print(json.dumps(output, indent=2))
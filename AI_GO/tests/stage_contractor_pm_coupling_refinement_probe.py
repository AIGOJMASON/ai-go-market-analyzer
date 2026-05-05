from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_service import (
    create_assumption,
)
from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_service import (
    create_decision,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_context,
    extract_target_context,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_refinement_layer import (
    attach_refinement_to_payload,
    build_coupling_refinement_context,
)


def run_probe() -> dict:
    project_id = "project-pm-coupling-refinement-probe"
    phase_id = "phase-pm-coupling-refinement-probe"
    assumption_id = "assumption-pm-coupling-refinement-probe-001"
    decision_id = "decision-pm-coupling-refinement-probe-001"

    assumption_result = create_assumption(
        {
            "actor": "stage_contractor_pm_coupling_refinement_probe",
            "entry_kwargs": {
                "assumption_id": assumption_id,
                "project_id": project_id,
                "statement": (
                    "Procurement lead time is assumed stable but remains unverified."
                ),
                "source_type": "Other",
                "source_reference": "stage_contractor_pm_coupling_refinement_probe",
                "logged_by": "AI_GO",
                "owner_acknowledged": "Not_Required",
                "validation_status": "Unverified",
                "impact_if_false": (
                    "Decision confidence should be cautious until procurement confirms lead time."
                ),
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],
                "linked_risk_ids": [],
                "notes": (
                    "Phase 2G.5 probe. Assumption should produce refinement context."
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

    assert refinement_context["artifact_type"] == "contractor_pm_coupling_refinement_context"
    assert refinement_context["packet_count"] == 1
    assert refinement_context["refinement_count"] == 1
    assert refinement_context["blocked_count"] == 0
    assert refinement_context["sealed"] is True

    refinement = refinement_context["refinements"][0]
    assert refinement["packet_governed"] is True
    assert refinement["source_type"] == "assumption"
    assert refinement["target_service"] == "decision"
    assert refinement["authority"]["execution_allowed"] is False
    assert refinement["authority"]["mutation_allowed"] is False
    assert refinement["authority"]["grants_authority"] is False
    assert (
        refinement["refinement"]["refinement_type"]
        == "assumption_uncertainty_refinement"
    )
    assert refinement["refinement"]["caution_level"] == "heightened_caution"
    assert refinement["refinement"]["application_mode"] == "annotate_and_require_lineage"

    decision_payload = attach_refinement_to_payload(
        payload={
            "actor": "stage_contractor_pm_coupling_refinement_probe",
            "pm_context": decision_pm_context,
            "entry_kwargs": {
                "decision_id": decision_id,
                "project_id": project_id,
                "title": "PM Coupling Refinement Probe Decision",
                "decision_type": "Risk_Acceptance",
                "phase_id": phase_id,
                "expected_risk_level": "Moderate",
                "notes_on_assumptions": (
                    "Decision received both pm_context and pm_refinement_context. "
                    "Refinement is annotation only and does not grant authority."
                ),
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": "PM coupling refinement probe",
                "notes_internal": (
                    "Phase 2G.5. Controlled influence application verified. "
                    "Service still executes through its own governance path."
                ),
                "attachments_refs": [],
            },
        },
        refinement_context=refinement_context,
    )

    decision_result = create_decision(decision_payload)

    assert decision_result["mode"] == "governed_execution"
    assert decision_result["status"] == "created"
    assert decision_result["state"]["valid"] is True
    assert decision_result["watcher"]["valid"] is True
    assert decision_result["execution_gate"]["allowed"] is True
    assert decision_result["entry"]["decision_id"] == decision_id
    assert decision_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert decision_result["result_summary"]["effect"] == "execution_completed"

    return {
        "status": "passed",
        "phase": "2G.5",
        "link": "controlled_influence_refinement",
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
            "packet_count": refinement_context["packet_count"],
            "refinement_count": refinement_context["refinement_count"],
            "blocked_count": refinement_context["blocked_count"],
            "first_refinement": refinement_context["refinements"][0],
        },
        "decision_downstream_validation": {
            "decision_id": decision_result["entry"]["decision_id"],
            "artifact_path": decision_result["artifact_path"],
            "receipt_path": decision_result["receipt_path"],
            "result_summary": decision_result["result_summary"],
        },
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_PM_COUPLING_REFINEMENT_PROBE: PASS")
    print(json.dumps(output, indent=2))
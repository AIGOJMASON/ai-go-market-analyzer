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


def run_probe() -> dict:
    project_id = "project-pm-coupling-assumption-fanout-probe"
    phase_id = "phase-pm-coupling-assumption-fanout-probe"
    assumption_id = "assumption-pm-coupling-fanout-probe-001"
    decision_id = "decision-pm-coupling-assumption-decision-probe-001"

    assumption_result = create_assumption(
        {
            "actor": "stage_contractor_pm_coupling_assumption_fanout_probe",
            "entry_kwargs": {
                "assumption_id": assumption_id,
                "project_id": project_id,
                "statement": (
                    "Material lead time is assumed stable until procurement "
                    "confirmation is received."
                ),
                "source_type": "Other",
                "source_reference": "stage_contractor_pm_coupling_assumption_fanout_probe",
                "logged_by": "AI_GO",
                "owner_acknowledged": "Not_Required",
                "validation_status": "Unverified",
                "impact_if_false": (
                    "Decision, risk, router, comply, and oracle context may need "
                    "re-evaluation if this assumption fails."
                ),
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],
                "linked_risk_ids": [],
                "notes": (
                    "Phase 2G.4 probe. Assumption should fan out through PM-owned "
                    "coupling packets only."
                ),
            },
        }
    )

    assert assumption_result["mode"] == "governed_execution"
    assert assumption_result["status"] == "created"
    assert assumption_result["state"]["valid"] is True
    assert assumption_result["watcher"]["valid"] is True
    assert assumption_result["execution_gate"]["allowed"] is True
    assert assumption_result["entry"]["project_id"] == project_id
    assert assumption_result["entry"]["assumption_id"] == assumption_id
    assert assumption_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert assumption_result["result_summary"]["effect"] == "execution_completed"

    coupling_context = build_pm_coupling_context(
        project_id=project_id,
        phase_id=phase_id,
        assumption_records=[assumption_result],
        actor="PM_CORE",
    )

    assert coupling_context["packet_count"] == 5

    expected_targets = {
        "oracle",
        "decision",
        "risk",
        "router",
        "comply",
    }

    actual_targets = set()
    for packet in coupling_context["packets"]:
        assert packet["source"]["source_type"] == "assumption"
        assert packet["target"]["allowed_use"] == "bounded_context_only"
        assert packet["authority"]["pm_owned"] is True
        assert packet["authority"]["downstream_execution_allowed"] is False
        assert packet["authority"]["downstream_mutation_allowed"] is False
        assert packet["authority"]["grants_authority"] is False
        assert packet["authority"]["requires_downstream_governance"] is True
        assert packet["authority"]["requires_downstream_watcher"] is True
        assert packet["authority"]["requires_downstream_execution_gate"] is True
        assert packet["constraints"]["no_lateral_service_call"] is True
        assert packet["constraints"]["no_direct_state_mutation"] is True
        assert packet["constraints"]["packet_remains_context_not_truth"] is True
        assert packet["sealed"] is True

        target_service = packet["target"]["target_service"]
        actual_targets.add(target_service)

        assert packet["influence"]["influence_type"] == f"assumption_to_{target_service}"
        assert packet["influence"]["assumption_context"]["assumption_id"] == assumption_id
        assert (
            packet["influence"]["assumption_context"]["validation_status"]
            == "Unverified"
        )

    assert actual_targets == expected_targets

    decision_pm_context = extract_target_context(
        coupling_context=coupling_context,
        target_service="decision",
    )

    assert decision_pm_context["packet_count"] == 1
    assert decision_pm_context["packets"][0]["source"]["source_type"] == "assumption"
    assert decision_pm_context["packets"][0]["target"]["target_service"] == "decision"

    decision_result = create_decision(
        {
            "actor": "stage_contractor_pm_coupling_assumption_fanout_probe",
            "pm_context": decision_pm_context,
            "entry_kwargs": {
                "decision_id": decision_id,
                "project_id": project_id,
                "title": "PM Coupling Assumption To Decision Probe",
                "decision_type": "Risk_Acceptance",
                "phase_id": phase_id,
                "expected_risk_level": "Moderate",
                "notes_on_assumptions": (
                    "Decision received assumption influence through pm_context only. "
                    "Assumption did not mutate decision directly."
                ),
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": (
                    "PM coupling assumption to decision probe"
                ),
                "notes_internal": (
                    "Phase 2G.4 downstream write validation. The decision service "
                    "still runs through its own governance, watcher, execution gate, "
                    "executor, receipt, and result summary."
                ),
                "attachments_refs": [],
            },
        }
    )

    assert decision_result["mode"] == "governed_execution"
    assert decision_result["status"] == "created"
    assert decision_result["state"]["valid"] is True
    assert decision_result["watcher"]["valid"] is True
    assert decision_result["execution_gate"]["allowed"] is True
    assert decision_result["entry"]["project_id"] == project_id
    assert decision_result["entry"]["decision_id"] == decision_id
    assert decision_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert decision_result["result_summary"]["effect"] == "execution_completed"
    assert decision_result["result_summary"]["counts"]["state_mutations"] == 1
    assert decision_result["result_summary"]["counts"]["artifacts_created"] == 1

    return {
        "status": "passed",
        "phase": "2G.4",
        "link": "assumption_to_everything",
        "assumption": {
            "assumption_id": assumption_result["entry"]["assumption_id"],
            "artifact_path": assumption_result["artifact_path"],
            "receipt_path": assumption_result["receipt_path"],
            "result_summary": assumption_result["result_summary"],
        },
        "coupling": {
            "context_hash": coupling_context["context_hash"],
            "packet_count": coupling_context["packet_count"],
            "targets": sorted(actual_targets),
            "by_target_counts": {
                target: len(coupling_context["by_target"][target])
                for target in sorted(expected_targets)
            },
            "first_packet_by_target": {
                target: coupling_context["by_target"][target][0]
                for target in sorted(expected_targets)
            },
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
    print("STAGE_CONTRACTOR_PM_COUPLING_ASSUMPTION_FANOUT_PROBE: PASS")
    print(json.dumps(output, indent=2))
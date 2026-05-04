from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_service import (
    create_decision,
)
from AI_GO.child_cores.contractor_builder_v1.pm_core.coupling_packet_builder import (
    build_pm_coupling_context,
    extract_target_context,
)
from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_service import (
    create_risk,
)


def run_probe() -> dict:
    project_id = "project-pm-coupling-decision-risk-probe"
    phase_id = "phase-pm-coupling-decision-risk-probe"
    decision_id = "decision-pm-coupling-decision-risk-probe-001"

    decision_result = create_decision(
        {
            "actor": "stage_contractor_pm_coupling_decision_to_risk_probe",
            "entry_kwargs": {
                "decision_id": decision_id,
                "project_id": project_id,
                "title": "PM Coupling Decision To Risk Probe",
                "decision_type": "Risk_Acceptance",
                "phase_id": phase_id,
                "expected_risk_level": "Moderate",
                "notes_on_assumptions": (
                    "Decision should be visible to risk as PM-owned context only."
                ),
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": "PM coupling decision to risk probe",
                "notes_internal": (
                    "Verify decision output can become bounded PM context for risk."
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
    assert decision_result["result_summary"]["artifact_type"] == "post_execution_result_summary"

    coupling_context = build_pm_coupling_context(
        project_id=project_id,
        phase_id=phase_id,
        decision_records=[decision_result],
        actor="PM_CORE",
    )

    risk_pm_context = extract_target_context(
        coupling_context=coupling_context,
        target_service="risk",
    )

    assert risk_pm_context["packet_count"] >= 1
    assert risk_pm_context["packets"][0]["source"]["source_type"] == "decision"
    assert risk_pm_context["packets"][0]["target"]["target_service"] == "risk"

    risk_result = create_risk(
        {
            "actor": "stage_contractor_pm_coupling_decision_to_risk_probe",
            "pm_context": risk_pm_context,
            "entry_kwargs": {
                "risk_id": "risk-pm-coupling-decision-risk-probe-001",
                "project_id": project_id,
                "category": "Other",
                "description": (
                    "Risk created with PM coupling context from a governed decision."
                ),
                "probability": "Moderate",
                "impact_level": "Moderate",
                "mitigation_strategy": (
                    "Review decision context before routing downstream schedule or "
                    "operational changes."
                ),
                "mitigation_owner": "Project Manager",
                "review_frequency": "weekly",
                "linked_decision_ids": [decision_id],
                "linked_change_packet_ids": [],
                "notes": (
                    "Phase 2G.2 probe. Risk received decision influence through "
                    "pm_context only. No direct decision-to-risk mutation occurred."
                ),
            },
        }
    )

    assert risk_result["mode"] == "governed_execution"
    assert risk_result["status"] == "created"
    assert risk_result["state"]["valid"] is True
    assert risk_result["watcher"]["valid"] is True
    assert risk_result["execution_gate"]["allowed"] is True
    assert risk_result["entry"]["project_id"] == project_id
    assert risk_result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert risk_result["result_summary"]["effect"] == "execution_completed"

    return {
        "status": "passed",
        "phase": "2G.2",
        "link": "decision_to_risk",
        "decision": {
            "decision_id": decision_result["entry"]["decision_id"],
            "artifact_path": decision_result["artifact_path"],
            "receipt_path": decision_result["receipt_path"],
            "result_summary": decision_result["result_summary"],
        },
        "coupling": {
            "context_hash": coupling_context["context_hash"],
            "packet_count": coupling_context["packet_count"],
            "risk_packet_count": risk_pm_context["packet_count"],
            "first_packet": risk_pm_context["packets"][0],
        },
        "risk": {
            "risk_id": risk_result["entry"]["risk_id"],
            "artifact_path": risk_result["artifact_path"],
            "receipt_path": risk_result["receipt_path"],
            "result_summary": risk_result["result_summary"],
        },
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_PM_COUPLING_DECISION_TO_RISK_PROBE: PASS")
    print(json.dumps(output, indent=2))
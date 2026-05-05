from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.decision_log.decision_service import (
    create_decision,
)


def run_probe() -> dict:
    result = create_decision(
        {
            "actor": "stage_contractor_decision_governed_probe",
            "entry_kwargs": {
                "decision_id": "decision-governed-probe-001",
                "project_id": "project-decision-governed-probe",
                "title": "Governed Decision Probe",
                "decision_type": "Schedule_Adjustment",
                "phase_id": "phase-decision-governed-probe",
                "linked_change_packet_id": "",
                "compliance_snapshot_id": "",
                "schedule_baseline_id": "",
                "budget_baseline_id": "",
                "drawing_revision_id": "",
                "oracle_snapshot_id": "",
                "expected_schedule_delta_days": 0.0,
                "expected_cost_delta_amount": 0.0,
                "expected_margin_delta_percent": None,
                "expected_risk_level": "Low",
                "notes_on_assumptions": "Phase 2F governed decision create probe.",
                "may_reference_in_owner_reports": True,
                "owner_report_reference_label": "Governed decision probe",
                "notes_internal": "Verify decision create runs through governed service.",
                "attachments_refs": [],
            },
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "created"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["execution_gate"]["allowed"] is True
    assert result["entry"]["project_id"] == "project-decision-governed-probe"
    assert result["entry"]["decision_id"] == "decision-governed-probe-001"
    assert result["artifact_path"]
    assert result["receipt_path"]
    assert result["result_summary"]["artifact_type"] == "post_execution_result_summary"

    return {
        "status": "passed",
        "governance_packet_id": result.get("governance_decision", {}).get("governance_packet_id"),
        "artifact_path": result["artifact_path"],
        "receipt_path": result["receipt_path"],
        "result_summary": result["result_summary"],
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_DECISION_GOVERNED_PROBE: PASS")
    print(json.dumps(output, indent=2))
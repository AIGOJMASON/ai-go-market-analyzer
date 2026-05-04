from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.risk_register.risk_service import create_risk


def run_probe() -> dict:
    result = create_risk(
        {
            "actor": "stage_contractor_risk_governed_probe",
            "entry_kwargs": {
                "risk_id": "risk-governed-probe-001",
                "project_id": "project-risk-governed-probe",

                # ✅ Correct schema fields (fixed)
                "category": "Other",
                "description": "Verify risk create runs through governed service.",
                "probability": "Low",
                "impact_level": "Low",
                "mitigation_strategy": "No production impact.",
                "mitigation_owner": "AI_GO",
                "review_frequency": "weekly",

                # Optional link fields
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],

                # Notes
                "notes": "Phase 2F governed risk create probe.",
            },
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "created"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["execution_gate"]["allowed"] is True

    assert result["entry"]["project_id"] == "project-risk-governed-probe"
    assert result["entry"]["risk_id"] == "risk-governed-probe-001"

    assert result["artifact_path"]
    assert result["receipt_path"]

    assert result["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert result["result_summary"]["effect"] == "execution_completed"
    assert result["result_summary"]["project_id"] == "project-risk-governed-probe"

    assert result["result_summary"]["counts"]["state_mutations"] == 1
    assert result["result_summary"]["counts"]["artifacts_created"] == 1

    return {
        "status": "passed",
        "governance_packet_id": result.get("governance_decision", {}).get("governance_packet_id"),
        "artifact_path": result["artifact_path"],
        "receipt_path": result["receipt_path"],
        "result_summary": result["result_summary"],
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_RISK_GOVERNED_PROBE: PASS")
    print(json.dumps(output, indent=2))
from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.assumption_log.assumption_service import (
    create_assumption,
)


def run_probe() -> dict:
    result = create_assumption(
        {
            "actor": "stage_contractor_assumption_governed_probe",
            "entry_kwargs": {
                "assumption_id": "assumption-governed-probe-001",
                "project_id": "project-assumption-governed-probe",
                "statement": "Verify assumption create runs through governed service.",
                "source_type": "Other",
                "source_reference": "stage_contractor_assumption_governed_probe",
                "logged_by": "AI_GO",
                "owner_acknowledged": "Not_Required",
                "validation_status": "Unverified",
                "impact_if_false": "Probe would fail if assumption governance is not wired.",
                "linked_decision_ids": [],
                "linked_change_packet_ids": [],
                "linked_risk_ids": [],
                "notes": "Phase 2F governed assumption create probe.",
            },
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "created"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["execution_gate"]["allowed"] is True
    assert result["entry"]["project_id"] == "project-assumption-governed-probe"
    assert result["entry"]["assumption_id"] == "assumption-governed-probe-001"
    assert result["artifact_path"]
    assert result["receipt_path"]
    assert result["result_summary"]["effect"] == "execution_completed"
    assert result["result_summary"]["project_id"] == "project-assumption-governed-probe"

    return {
        "status": "passed",
        "governance_packet_id": result.get("governance_decision", {}).get("governance_packet_id"),
        "artifact_path": result["artifact_path"],
        "receipt_path": result["receipt_path"],
        "result_summary": result["result_summary"],
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_ASSUMPTION_GOVERNED_PROBE: PASS")
    print(json.dumps(output, indent=2))
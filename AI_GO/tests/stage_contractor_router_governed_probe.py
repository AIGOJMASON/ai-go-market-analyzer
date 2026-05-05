from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.router.router_service import (
    persist_schedule_blocks_governed,
)


def run_probe() -> dict:
    result = persist_schedule_blocks_governed(
        {
            "actor": "stage_contractor_router_governed_probe",
            "project_id": "project-router-governed-probe",
            "blocks": [
                {
                    "block_id": "block-router-governed-probe-001",
                    "project_id": "project-router-governed-probe",
                    "phase_id": "phase-router-governed-probe",

                    # ✅ REQUIRED FIX
                    "block_type": "Crew_Assignment",

                    "crew_id": "crew-demo",
                    "trade": "Electrical",
                    "start_date": "2026-04-29",
                    "end_date": "2026-04-30",
                    "status": "planned",
                    "notes": "Phase 2F governed router block probe.",
                }
            ],
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "stored"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["execution_gate"]["allowed"] is True
    assert result["project_id"] == "project-router-governed-probe"
    assert result["artifact_path"]
    assert result["receipt_path"]
    assert result["result_summary"]["effect"] == "execution_completed"
    assert result["result_summary"]["project_id"] == "project-router-governed-probe"
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
    print("STAGE_CONTRACTOR_ROUTER_GOVERNED_PROBE: PASS")
    print(json.dumps(output, indent=2))
from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.oracle.market_snapshot_registry import (
    list_registered_snapshots,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.oracle_service import (
    run_oracle_projection_governed,
)


def run_probe() -> dict:
    snapshots = list_registered_snapshots()
    assert snapshots, "No registered oracle snapshots found."

    first_snapshot = snapshots[0]
    snapshot_id = str(first_snapshot.get("snapshot_id", "")).strip()
    market_domain = str(first_snapshot.get("market_domain", "")).strip()

    assert snapshot_id, "Registered snapshot is missing snapshot_id."
    assert market_domain, "Registered snapshot is missing market_domain."

    result = run_oracle_projection_governed(
        {
            "actor": "stage_contractor_oracle_governed_probe",
            "project_id": "project-oracle-governed-probe",
            "snapshot_id": snapshot_id,
            "exposure_profile_id": "exposure-profile-oracle-governed-probe",
            "domain_exposure": {
                market_domain: "High",
            },
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "completed"
    assert result["state"]["valid"] is True
    assert result["watcher"]["valid"] is True
    assert result["execution_gate"]["allowed"] is True
    assert result["project_id"] == "project-oracle-governed-probe"
    assert result["artifact_path"]
    assert result["receipt_path"]
    assert result["result_summary"]["effect"] == "execution_completed"
    assert result["result_summary"]["project_id"] == "project-oracle-governed-probe"

    return {
        "status": "passed",
        "snapshot_id_used": snapshot_id,
        "market_domain_used": market_domain,
        "governance_packet_id": result.get("governance_decision", {}).get("governance_packet_id"),
        "artifact_path": result["artifact_path"],
        "receipt_path": result["receipt_path"],
        "result_summary": result["result_summary"],
    }


if __name__ == "__main__":
    output = run_probe()
    print("STAGE_CONTRACTOR_ORACLE_GOVERNED_PROBE: PASS")
    print(json.dumps(output, indent=2))
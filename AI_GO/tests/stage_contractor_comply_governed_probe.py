from __future__ import annotations

import json

from AI_GO.child_cores.contractor_builder_v1.comply.comply_service import (
    run_compliance_check,
)


def run_probe() -> dict:
    result = run_compliance_check(
        {
            "actor": "stage_contractor_comply_probe",
            "project_id": "project-comply-probe",
            "payload": {
                "check_type": "basic",
                "notes": "Phase 2F compliance probe",
            },
        }
    )

    assert result["mode"] == "governed_execution"
    assert result["status"] == "completed"
    assert result["execution_gate"]["allowed"] is True
    assert result["artifact_path"]
    assert result["receipt_path"]

    return {
        "status": "passed",
        "result_summary": result["result_summary"],
    }


if __name__ == "__main__":
    out = run_probe()
    print("STAGE_CONTRACTOR_COMPLY_GOVERNED_PROBE: PASS")
    print(json.dumps(out, indent=2))
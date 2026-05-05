# AI_GO/tests/stage_governance_hardening_probe.py

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    from AI_GO.core.paths.path_resolver import (
        get_project_root,
        get_state_root,
        get_receipts_root,
    )
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
    from AI_GO.core.execution_gate.runtime_execution_gate import (
        evaluate_execution_gate,
        enforce_execution_gate,
    )
    from AI_GO.core.governance.governance_explainer import explain_governance_packet

    project_root = get_project_root()
    state_root = get_state_root()
    receipts_root = get_receipts_root()

    assert project_root.exists(), "project_root_missing"
    assert state_root.exists(), "state_root_missing"
    assert receipts_root.exists(), "receipts_root_missing"

    receipt_result = write_contractor_receipt(
        module_name="hardening_probe",
        event_type="probe_receipt_write",
        receipt={
            "probe": "stage_governance_hardening_probe",
            "status": "running",
        },
    )

    receipt_path = Path(receipt_result["global_path"])
    assert receipt_path.exists(), "receipt_not_written"

    gate = evaluate_execution_gate(
        watcher={"status": "passed", "valid": True},
        state={"status": "passed", "valid": True},
        canon={
            "status": "passed",
            "valid": True,
            "execution_allowed": True,
            "approval_required": False,
        },
        request={
            "request_id": "hardening-probe-001",
            "route": "probe://governance-hardening",
            "action": "probe",
        },
    )

    assert gate["allowed"] is True, gate
    enforce_execution_gate(gate)

    explanation = explain_governance_packet(
        {
            "watcher": {"status": "passed", "valid": True},
            "state": {"status": "passed", "valid": True},
            "canon": {
                "status": "passed",
                "valid": True,
                "execution_allowed": True,
            },
            "execution_gate": gate,
            "execution_result": {
                "status": "ok",
                "receipt_path": str(receipt_path),
            },
        }
    )

    assert explanation["status"] == "ok", explanation
    assert explanation["mode"] == "observer_only", explanation
    assert explanation["execution_allowed"] is False, explanation

    print(
        json.dumps(
            {
                "status": "passed",
                "project_root": str(project_root),
                "state_root": str(state_root),
                "receipts_root": str(receipts_root),
                "receipt_path": str(receipt_path),
                "execution_gate": gate,
                "governance_explanation": explanation,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
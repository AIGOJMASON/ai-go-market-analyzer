from __future__ import annotations

from AI_GO.core.governance.governance_packet_store import (
    attach_result_summary_to_governance_packet,
    load_governance_packet,
    persist_governance_packet,
)
from AI_GO.core.governance.result_summary import build_result_summary


def run_probe() -> dict:
    packet = {
        "artifact_type": "governed_request_packet",
        "artifact_version": "v2",
        "governor_version": "v2.0",
        "created_at": "2026-04-29T00:00:00+00:00",
        "profile": "contractor_phase_closeout",
        "action": "phase_closeout",
        "project_id": "project-result-summary-probe",
        "phase_id": "phase-result-summary-probe",
        "status": "allowed",
        "allowed": True,
        "request": {
            "request_id": "request-result-summary-probe",
            "route": "/contractor-builder/phase-closeout/run",
            "project_id": "project-result-summary-probe",
            "phase_id": "phase-result-summary-probe",
        },
        "watcher": {"status": "passed", "valid": True},
        "state": {"status": "passed", "valid": True},
        "canon": {"status": "passed", "valid": True},
        "execution_gate": {"status": "passed", "valid": True, "allowed": True},
        "sealed": True,
    }

    persisted = persist_governance_packet(
        packet=packet,
        profile="contractor_phase_closeout",
    )

    packet_id = persisted["governance_packet_id"]

    result_summary = build_result_summary(
        action="phase_closeout",
        context={
            "project_id": "project-result-summary-probe",
            "phase_id": "phase-result-summary-probe",
        },
        result={
            "status": "delivery_failed",
            "pdf_artifact_record_path": "state/demo/pdf.artifact.json",
            "document_receipts": {
                "global_receipt_path": "receipts/demo/pdf.json",
                "project_receipt_path": "state/demo/project_pdf_receipt.json",
            },
            "email_result": {
                "status": "failed",
                "provider": "smtp",
                "recipient": "client@example.com",
                "delivery_id": "email_probe",
                "execution_gate_allowed": True,
            },
            "email_record_path": "state/demo/email.json",
            "delivery_receipts": {
                "global_receipt_path": "receipts/demo/delivery.json",
                "project_receipt_path": "state/demo/project_delivery_receipt.json",
            },
        },
    )

    attached = attach_result_summary_to_governance_packet(
        profile="contractor_phase_closeout",
        governance_packet_id=packet_id,
        result_summary=result_summary,
    )

    loaded = load_governance_packet(
        profile="contractor_phase_closeout",
        governance_packet_id=packet_id,
    )

    assert attached["status"] == "attached"
    assert loaded["result_summary"]["artifact_type"] == "post_execution_result_summary"
    assert loaded["result_summary"]["status"] == "delivery_failed"
    assert loaded["result_summary"]["effect"] == "execution_partial_delivery_failed"
    assert loaded["post_execution_result_summary_attached"] is True

    return {
        "status": "passed",
        "governance_packet_id": packet_id,
        "result_summary": loaded["result_summary"],
        "packet_path": attached["path"],
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_RESULT_SUMMARY_PROBE: PASS")
    print(result)
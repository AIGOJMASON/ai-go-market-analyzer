from __future__ import annotations

from AI_GO.core.runtime.closeout.case_closeout_record import (
    CaseCloseoutRecordError,
    build_case_closeout_record,
)


def _case_resolution(case_id: str, sealed: bool = True) -> dict:
    return {
        "artifact_type": "case_resolution",
        "payload": {
            "case_resolution_id": f"WR-CASE-RESOLUTION-{case_id}",
            "case_id": case_id,
            "audit_replay_index_id": f"WR-AUDIT-REPLAY-{case_id}",
            "created_at": "2026-03-20T00:00:00Z",
            "issuing_authority": "RUNTIME_CASE_RESOLUTION",
            "final_state": "success",
            "source_path": "primary",
            "authoritative_receipt_id": f"WR-RECEIPT-{case_id}",
            "payload_class": "runtime_report_bundle",
            "route_class": "internal_handoff",
            "execution_mode": "governed_runtime",
            "actionable": True,
            "instruction": "downstream_dispatch_permitted",
            "resolution_basis": "primary",
            "discarded_paths": [],
            "resolution_confidence": "bounded",
            "closure_status": "grace_applied",
            "observed_branches": ["primary"],
            "replay_chain_length": 1,
            "sealed": sealed,
        },
    }


def _dispatch_packet(case_id: str, sealed: bool = True, dispatch_ready: bool = True) -> dict:
    return {
        "artifact_type": "child_core_dispatch_packet",
        "payload": {
            "dispatch_packet_id": f"WR-CHILD-DISPATCH-{case_id}",
            "case_id": case_id,
            "case_resolution_id": f"WR-CASE-RESOLUTION-{case_id}",
            "created_at": "2026-03-20T00:01:00Z",
            "issuing_authority": "RUNTIME_CHILD_CORE_DISPATCH",
            "target_child_core": "proposal_saas",
            "dispatch_ready": dispatch_ready,
            "instruction": "generate_proposal",
            "final_state": "success",
            "source_path": "primary",
            "payload_class": "runtime_report_bundle",
            "route_class": "internal_handoff",
            "execution_mode": "governed_runtime",
            "resolution_confidence": "bounded",
            "authoritative_receipt_id": f"WR-RECEIPT-{case_id}",
            "observed_branches": ["primary"],
            "dispatch_note": None,
            "sealed": sealed,
        },
    }


def _intake_receipt(
    case_id: str,
    intake_decision: str = "accepted",
    sealed: bool = True,
) -> dict:
    intake_status = (
        "child_core_intake_accepted"
        if intake_decision == "accepted"
        else "child_core_intake_rejected"
    )
    return {
        "artifact_type": "child_core_intake_receipt",
        "payload": {
            "intake_receipt_id": f"WR-CHILD-INTAKE-{case_id}",
            "case_id": case_id,
            "case_resolution_id": f"WR-CASE-RESOLUTION-{case_id}",
            "dispatch_packet_id": f"WR-CHILD-DISPATCH-{case_id}",
            "created_at": "2026-03-20T00:02:00Z",
            "issuing_authority": "RUNTIME_CHILD_CORE_INTAKE",
            "target_child_core": "proposal_saas",
            "intake_decision": intake_decision,
            "intake_status": intake_status,
            "accepted_by": "proposal_saas_intake",
            "intake_reason": None if intake_decision == "accepted" else "capacity_unavailable",
            "instruction": "generate_proposal",
            "final_state": "success",
            "source_path": "primary",
            "payload_class": "runtime_report_bundle",
            "route_class": "internal_handoff",
            "execution_mode": "governed_runtime",
            "resolution_confidence": "bounded",
            "authoritative_receipt_id": f"WR-RECEIPT-{case_id}",
            "observed_branches": ["primary"],
            "actionable_downstream": intake_decision == "accepted",
            "sealed": sealed,
        },
    }


def _expect_pass(case_name: str, fn) -> dict:
    try:
        fn()
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def _expect_fail(case_name: str, fn) -> dict:
    try:
        fn()
        return {"case": case_name, "status": "failed", "error": "expected failure but passed"}
    except CaseCloseoutRecordError:
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def run_stage56_case_closeout_record_probe() -> dict:
    results = []

    def case_01_valid_closed_accepted():
        record = build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5601"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5601"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5601", intake_decision="accepted"),
        )
        assert record["artifact_type"] == "case_closeout_record"
        assert record["payload"]["closeout_state"] == "closed_accepted"

    results.append(_expect_pass("case_01_valid_closed_accepted", case_01_valid_closed_accepted))

    def case_02_valid_closed_rejected():
        record = build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5602"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5602"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5602", intake_decision="rejected"),
        )
        assert record["payload"]["closeout_state"] == "closed_rejected"
        assert record["payload"]["intake_decision"] == "rejected"

    results.append(_expect_pass("case_02_valid_closed_rejected", case_02_valid_closed_rejected))

    def case_03_reject_invalid_case_resolution_artifact_type():
        build_case_closeout_record(
            case_resolution={"artifact_type": "audit_replay_index", "payload": {}},
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5603"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5603"),
        )

    results.append(_expect_fail("case_03_reject_invalid_case_resolution_artifact_type", case_03_reject_invalid_case_resolution_artifact_type))

    def case_04_reject_case_id_mismatch():
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5604-A"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5604-B"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5604-B"),
        )

    results.append(_expect_fail("case_04_reject_case_id_mismatch", case_04_reject_case_id_mismatch))

    def case_05_reject_dispatch_resolution_mismatch():
        packet = _dispatch_packet("WR-CASE-5605")
        packet["payload"]["case_resolution_id"] = "WR-CASE-RESOLUTION-OTHER"
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5605"),
            child_core_dispatch_packet=packet,
            child_core_intake_receipt=_intake_receipt("WR-CASE-5605"),
        )

    results.append(_expect_fail("case_05_reject_dispatch_resolution_mismatch", case_05_reject_dispatch_resolution_mismatch))

    def case_06_reject_intake_dispatch_mismatch():
        receipt = _intake_receipt("WR-CASE-5606")
        receipt["payload"]["dispatch_packet_id"] = "WR-CHILD-DISPATCH-OTHER"
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5606"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5606"),
            child_core_intake_receipt=receipt,
        )

    results.append(_expect_fail("case_06_reject_intake_dispatch_mismatch", case_06_reject_intake_dispatch_mismatch))

    def case_07_reject_unsealed_resolution():
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5607", sealed=False),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5607"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5607"),
        )

    results.append(_expect_fail("case_07_reject_unsealed_resolution", case_07_reject_unsealed_resolution))

    def case_08_reject_dispatch_not_ready():
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5608"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5608", dispatch_ready=False),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5608"),
        )

    results.append(_expect_fail("case_08_reject_dispatch_not_ready", case_08_reject_dispatch_not_ready))

    def case_09_reject_target_child_core_mismatch():
        receipt = _intake_receipt("WR-CASE-5609")
        receipt["payload"]["target_child_core"] = "gis"
        build_case_closeout_record(
            case_resolution=_case_resolution("WR-CASE-5609"),
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5609"),
            child_core_intake_receipt=receipt,
        )

    results.append(_expect_fail("case_09_reject_target_child_core_mismatch", case_09_reject_target_child_core_mismatch))

    def case_10_reject_internal_field_leakage():
        resolution = _case_resolution("WR-CASE-5610")
        resolution["payload"]["_internal"] = {"unsafe": True}
        build_case_closeout_record(
            case_resolution=resolution,
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5610"),
            child_core_intake_receipt=_intake_receipt("WR-CASE-5610"),
        )

    results.append(_expect_fail("case_10_reject_internal_field_leakage", case_10_reject_internal_field_leakage))

    passed = sum(1 for result in results if result["status"] == "passed")
    failed = sum(1 for result in results if result["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_stage56_case_closeout_record_probe())
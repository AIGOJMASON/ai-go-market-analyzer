from __future__ import annotations

from AI_GO.core.runtime.child_intake.child_core_intake_receipt import (
    ChildCoreIntakeReceiptError,
    build_child_core_intake_receipt,
)


def _dispatch_packet(
    case_id: str,
    target_child_core: str = "proposal_saas",
    dispatch_ready: bool = True,
    sealed: bool = True,
) -> dict:
    return {
        "artifact_type": "child_core_dispatch_packet",
        "payload": {
            "dispatch_packet_id": f"WR-CHILD-DISPATCH-{case_id}",
            "case_id": case_id,
            "case_resolution_id": f"WR-CASE-RESOLUTION-{case_id}",
            "created_at": "2026-03-19T23:00:00Z",
            "issuing_authority": "RUNTIME_CHILD_CORE_DISPATCH",
            "target_child_core": target_child_core,
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
    except ChildCoreIntakeReceiptError:
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def run_stage55_child_core_intake_receipt_probe() -> dict:
    results = []

    def case_01_valid_accepted_intake():
        receipt = build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5501"),
            intake_decision="accepted",
            accepted_by="proposal_saas_intake",
        )
        assert receipt["artifact_type"] == "child_core_intake_receipt"
        assert receipt["payload"]["intake_status"] == "child_core_intake_accepted"
        assert receipt["payload"]["actionable_downstream"] is True

    results.append(_expect_pass("case_01_valid_accepted_intake", case_01_valid_accepted_intake))

    def case_02_valid_rejected_intake():
        receipt = build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5502"),
            intake_decision="rejected",
            intake_reason="capacity_unavailable",
            accepted_by="proposal_saas_intake",
        )
        assert receipt["payload"]["intake_status"] == "child_core_intake_rejected"
        assert receipt["payload"]["actionable_downstream"] is False
        assert receipt["payload"]["intake_reason"] == "capacity_unavailable"

    results.append(_expect_pass("case_02_valid_rejected_intake", case_02_valid_rejected_intake))

    def case_03_valid_gis_acceptance():
        receipt = build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet(
                "WR-CASE-5503",
                target_child_core="gis",
            ),
            intake_decision="accepted",
            accepted_by="gis_intake",
        )
        assert receipt["payload"]["target_child_core"] == "gis"

    results.append(_expect_pass("case_03_valid_gis_acceptance", case_03_valid_gis_acceptance))

    def case_04_reject_invalid_artifact_type():
        build_child_core_intake_receipt(
            child_core_dispatch_packet={"artifact_type": "case_resolution", "payload": {}},
            intake_decision="accepted",
        )

    results.append(_expect_fail("case_04_reject_invalid_artifact_type", case_04_reject_invalid_artifact_type))

    def case_05_reject_unsealed_dispatch_packet():
        build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5505", sealed=False),
            intake_decision="accepted",
        )

    results.append(_expect_fail("case_05_reject_unsealed_dispatch_packet", case_05_reject_unsealed_dispatch_packet))

    def case_06_reject_dispatch_not_ready():
        build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5506", dispatch_ready=False),
            intake_decision="accepted",
        )

    results.append(_expect_fail("case_06_reject_dispatch_not_ready", case_06_reject_dispatch_not_ready))

    def case_07_reject_unapproved_target():
        build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet(
                "WR-CASE-5507",
                target_child_core="unknown_core",
            ),
            intake_decision="accepted",
        )

    results.append(_expect_fail("case_07_reject_unapproved_target", case_07_reject_unapproved_target))

    def case_08_reject_invalid_intake_decision():
        build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5508"),
            intake_decision="pending",
        )

    results.append(_expect_fail("case_08_reject_invalid_intake_decision", case_08_reject_invalid_intake_decision))

    def case_09_reject_rejected_without_reason():
        build_child_core_intake_receipt(
            child_core_dispatch_packet=_dispatch_packet("WR-CASE-5509"),
            intake_decision="rejected",
        )

    results.append(_expect_fail("case_09_reject_rejected_without_reason", case_09_reject_rejected_without_reason))

    def case_10_reject_internal_field_leakage():
        packet = _dispatch_packet("WR-CASE-5510")
        packet["payload"]["_internal"] = {"unsafe": True}
        build_child_core_intake_receipt(
            child_core_dispatch_packet=packet,
            intake_decision="accepted",
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
    print(run_stage55_child_core_intake_receipt_probe())
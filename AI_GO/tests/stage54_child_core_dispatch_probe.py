from __future__ import annotations

from AI_GO.core.runtime.child_dispatch.child_core_dispatch import (
    ChildCoreDispatchError,
    build_child_core_dispatch_packet,
)


def _case_resolution(
    case_id: str,
    final_state: str = "success",
    actionable: bool = True,
    sealed: bool = True,
    payload_class: str = "runtime_report_bundle",
    route_class: str = "internal_handoff",
    instruction: str = "downstream_dispatch_permitted",
) -> dict:
    return {
        "artifact_type": "case_resolution",
        "payload": {
            "case_resolution_id": f"WR-CASE-RESOLUTION-{case_id}",
            "case_id": case_id,
            "audit_replay_index_id": f"WR-AUDIT-REPLAY-{case_id}",
            "created_at": "2026-03-19T22:00:00Z",
            "issuing_authority": "RUNTIME_CASE_RESOLUTION",
            "final_state": final_state,
            "source_path": "primary" if final_state == "success" else "retry",
            "authoritative_receipt_id": f"WR-RECEIPT-{case_id}",
            "payload_class": payload_class,
            "route_class": route_class,
            "execution_mode": "governed_runtime",
            "actionable": actionable,
            "instruction": instruction,
            "resolution_basis": "primary",
            "discarded_paths": [],
            "resolution_confidence": "bounded",
            "closure_status": "grace_applied",
            "observed_branches": ["primary"],
            "replay_chain_length": 1,
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
    except ChildCoreDispatchError:
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def run_stage54_child_core_dispatch_probe() -> dict:
    results = []

    def case_01_valid_proposal_dispatch():
        packet = build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5401"),
            target_child_core="proposal_saas",
        )
        assert packet["artifact_type"] == "child_core_dispatch_packet"
        assert packet["payload"]["dispatch_ready"] is True
        assert packet["payload"]["instruction"] == "generate_proposal"

    results.append(_expect_pass("case_01_valid_proposal_dispatch", case_01_valid_proposal_dispatch))

    def case_02_valid_gis_dispatch():
        packet = build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5402"),
            target_child_core="gis",
        )
        assert packet["payload"]["target_child_core"] == "gis"
        assert packet["payload"]["instruction"] == "generate_mapping_action"

    results.append(_expect_pass("case_02_valid_gis_dispatch", case_02_valid_gis_dispatch))

    def case_03_valid_wru_escalated_dispatch():
        packet = build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5403", final_state="escalated"),
            target_child_core="wru",
        )
        assert packet["payload"]["instruction"] == "review_then_generate_learning_asset"
        assert packet["payload"]["final_state"] == "escalated"

    results.append(_expect_pass("case_03_valid_wru_escalated_dispatch", case_03_valid_wru_escalated_dispatch))

    def case_04_reject_invalid_artifact_type():
        build_child_core_dispatch_packet(
            case_resolution={"artifact_type": "audit_replay_index", "payload": {}},
            target_child_core="proposal_saas",
        )

    results.append(_expect_fail("case_04_reject_invalid_artifact_type", case_04_reject_invalid_artifact_type))

    def case_05_reject_unactionable_case_resolution():
        build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5405", actionable=False),
            target_child_core="proposal_saas",
        )

    results.append(_expect_fail("case_05_reject_unactionable_case_resolution", case_05_reject_unactionable_case_resolution))

    def case_06_reject_unsealed_case_resolution():
        build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5406", sealed=False),
            target_child_core="proposal_saas",
        )

    results.append(_expect_fail("case_06_reject_unsealed_case_resolution", case_06_reject_unsealed_case_resolution))

    def case_07_reject_unapproved_target_child_core():
        build_child_core_dispatch_packet(
            case_resolution=_case_resolution(case_id="WR-CASE-5407"),
            target_child_core="unknown_core",
        )

    results.append(_expect_fail("case_07_reject_unapproved_target_child_core", case_07_reject_unapproved_target_child_core))

    def case_08_reject_payload_class_mismatch():
        build_child_core_dispatch_packet(
            case_resolution=_case_resolution(
                case_id="WR-CASE-5408",
                payload_class="unsupported_payload",
            ),
            target_child_core="proposal_saas",
        )

    results.append(_expect_fail("case_08_reject_payload_class_mismatch", case_08_reject_payload_class_mismatch))

    def case_09_reject_terminal_failure_resolution():
        build_child_core_dispatch_packet(
            case_resolution=_case_resolution(
                case_id="WR-CASE-5409",
                final_state="terminal_failure",
                actionable=False,
            ),
            target_child_core="proposal_saas",
        )

    results.append(_expect_fail("case_09_reject_terminal_failure_resolution", case_09_reject_terminal_failure_resolution))

    def case_10_reject_internal_field_leakage():
        resolution = _case_resolution(case_id="WR-CASE-5410")
        resolution["payload"]["_internal"] = {"unsafe": True}
        build_child_core_dispatch_packet(
            case_resolution=resolution,
            target_child_core="proposal_saas",
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
    print(run_stage54_child_core_dispatch_probe())
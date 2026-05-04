from __future__ import annotations

from AI_GO.core.runtime.audit.audit_replay_index import (
    AuditReplayIndexError,
    build_audit_replay_index,
)


def _receipt(
    artifact_type: str,
    receipt_id: str,
    case_id: str,
    occurred_at: str,
    outcome_status: str,
    branch_class: str,
) -> dict:
    return {
        "artifact_type": artifact_type,
        "payload": {
            "receipt_id": receipt_id,
            "case_id": case_id,
            "occurred_at": occurred_at,
            "route_class": "internal_handoff",
            "payload_class": "runtime_report_bundle",
            "execution_mode": "governed_runtime",
            "outcome_status": outcome_status,
            "branch_class": branch_class,
            "result_ref": f"{receipt_id}__RESULT",
            "source_receipt_ref": f"{receipt_id}__SOURCE",
            "adapter_class": "internal_adapter",
            "adapter_ref": f"{receipt_id}__ADAPTER",
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
    except AuditReplayIndexError:
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def run_stage52_audit_replay_index_probe() -> dict:
    results = []

    def case_01_valid_delivery_only():
        index = build_audit_replay_index(
            delivery_outcome_receipt=_receipt(
                artifact_type="delivery_outcome_receipt",
                receipt_id="WR-DELIVERY-OUTCOME-0001",
                case_id="WR-CASE-0001",
                occurred_at="2026-03-19T20:00:00Z",
                outcome_status="delivered",
                branch_class="primary",
            )
        )
        assert index["artifact_type"] == "audit_replay_index"
        assert index["payload"]["branch_count"] == 1
        assert index["payload"]["observed_branches"] == ["primary"]

    results.append(_expect_pass("case_01_valid_delivery_only", case_01_valid_delivery_only))

    def case_02_valid_delivery_retry_chain():
        index = build_audit_replay_index(
            delivery_outcome_receipt=_receipt(
                artifact_type="delivery_outcome_receipt",
                receipt_id="WR-DELIVERY-OUTCOME-0002",
                case_id="WR-CASE-0002",
                occurred_at="2026-03-19T20:01:00Z",
                outcome_status="delivery_failed",
                branch_class="primary",
            ),
            retry_outcome_receipt=_receipt(
                artifact_type="retry_outcome_receipt",
                receipt_id="WR-RETRY-OUTCOME-0002",
                case_id="WR-CASE-0002",
                occurred_at="2026-03-19T20:02:00Z",
                outcome_status="retry_succeeded",
                branch_class="retry",
            ),
        )
        assert index["payload"]["branch_count"] == 2
        assert index["payload"]["latest_receipt_id"] == "WR-RETRY-OUTCOME-0002"

    results.append(_expect_pass("case_02_valid_delivery_retry_chain", case_02_valid_delivery_retry_chain))

    def case_03_valid_full_replay_chain():
        index = build_audit_replay_index(
            delivery_outcome_receipt=_receipt(
                artifact_type="delivery_outcome_receipt",
                receipt_id="WR-DELIVERY-OUTCOME-0003",
                case_id="WR-CASE-0003",
                occurred_at="2026-03-19T20:03:00Z",
                outcome_status="delivery_failed",
                branch_class="primary",
            ),
            retry_outcome_receipt=_receipt(
                artifact_type="retry_outcome_receipt",
                receipt_id="WR-RETRY-OUTCOME-0003",
                case_id="WR-CASE-0003",
                occurred_at="2026-03-19T20:04:00Z",
                outcome_status="retry_failed",
                branch_class="retry",
            ),
            escalation_outcome_receipt=_receipt(
                artifact_type="escalation_outcome_receipt",
                receipt_id="WR-ESCALATION-OUTCOME-0003",
                case_id="WR-CASE-0003",
                occurred_at="2026-03-19T20:05:00Z",
                outcome_status="escalation_completed",
                branch_class="escalation",
            ),
        )
        assert index["payload"]["branch_count"] == 3
        assert index["payload"]["observed_branches"] == ["primary", "retry", "escalation"]
        assert index["payload"]["replay_chain"][2]["branch_class"] == "escalation"

    results.append(_expect_pass("case_03_valid_full_replay_chain", case_03_valid_full_replay_chain))

    def case_04_reject_missing_required_field():
        receipt = _receipt(
            artifact_type="delivery_outcome_receipt",
            receipt_id="WR-DELIVERY-OUTCOME-0004",
            case_id="WR-CASE-0004",
            occurred_at="2026-03-19T20:06:00Z",
            outcome_status="delivered",
            branch_class="primary",
        )
        del receipt["payload"]["route_class"]
        build_audit_replay_index(delivery_outcome_receipt=receipt)

    results.append(_expect_fail("case_04_reject_missing_required_field", case_04_reject_missing_required_field))

    def case_05_reject_invalid_delivery_artifact_type():
        receipt = _receipt(
            artifact_type="transport_execution_result",
            receipt_id="WR-DELIVERY-OUTCOME-0005",
            case_id="WR-CASE-0005",
            occurred_at="2026-03-19T20:07:00Z",
            outcome_status="delivered",
            branch_class="primary",
        )
        build_audit_replay_index(delivery_outcome_receipt=receipt)

    results.append(_expect_fail("case_05_reject_invalid_delivery_artifact_type", case_05_reject_invalid_delivery_artifact_type))

    def case_06_reject_case_id_mismatch():
        build_audit_replay_index(
            delivery_outcome_receipt=_receipt(
                artifact_type="delivery_outcome_receipt",
                receipt_id="WR-DELIVERY-OUTCOME-0006",
                case_id="WR-CASE-0006-A",
                occurred_at="2026-03-19T20:08:00Z",
                outcome_status="delivery_failed",
                branch_class="primary",
            ),
            retry_outcome_receipt=_receipt(
                artifact_type="retry_outcome_receipt",
                receipt_id="WR-RETRY-OUTCOME-0006",
                case_id="WR-CASE-0006-B",
                occurred_at="2026-03-19T20:09:00Z",
                outcome_status="retry_succeeded",
                branch_class="retry",
            ),
        )

    results.append(_expect_fail("case_06_reject_case_id_mismatch", case_06_reject_case_id_mismatch))

    def case_07_reject_internal_field_leakage():
        receipt = _receipt(
            artifact_type="delivery_outcome_receipt",
            receipt_id="WR-DELIVERY-OUTCOME-0007",
            case_id="WR-CASE-0007",
            occurred_at="2026-03-19T20:10:00Z",
            outcome_status="delivered",
            branch_class="primary",
        )
        receipt["payload"]["_internal"] = {"unsafe": True}
        build_audit_replay_index(delivery_outcome_receipt=receipt)

    results.append(_expect_fail("case_07_reject_internal_field_leakage", case_07_reject_internal_field_leakage))

    def case_08_reject_invalid_branch_class_for_retry():
        retry_receipt = _receipt(
            artifact_type="retry_outcome_receipt",
            receipt_id="WR-RETRY-OUTCOME-0008",
            case_id="WR-CASE-0008",
            occurred_at="2026-03-19T20:12:00Z",
            outcome_status="retry_succeeded",
            branch_class="primary",
        )
        build_audit_replay_index(
            delivery_outcome_receipt=_receipt(
                artifact_type="delivery_outcome_receipt",
                receipt_id="WR-DELIVERY-OUTCOME-0008",
                case_id="WR-CASE-0008",
                occurred_at="2026-03-19T20:11:00Z",
                outcome_status="delivery_failed",
                branch_class="primary",
            ),
            retry_outcome_receipt=retry_receipt,
        )

    results.append(_expect_fail("case_08_reject_invalid_branch_class_for_retry", case_08_reject_invalid_branch_class_for_retry))

    passed = sum(1 for result in results if result["status"] == "passed")
    failed = sum(1 for result in results if result["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_stage52_audit_replay_index_probe())
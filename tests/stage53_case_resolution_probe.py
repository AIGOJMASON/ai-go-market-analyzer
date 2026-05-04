from __future__ import annotations

from AI_GO.core.runtime.resolution.case_resolution import (
    CaseResolutionError,
    build_case_resolution,
)


def _audit_replay_index(
    case_id: str,
    replay_chain: list[dict],
) -> dict:
    return {
        "artifact_type": "audit_replay_index",
        "payload": {
            "audit_replay_index_id": f"WR-AUDIT-REPLAY-{case_id}",
            "case_id": case_id,
            "created_at": "2026-03-19T21:00:00Z",
            "issuing_authority": "RUNTIME_AUDIT_REPLAY",
            "replay_chain": replay_chain,
            "replay_order": [entry["receipt_id"] for entry in replay_chain],
            "replay_refs": {
                "delivery_outcome_receipt_id": replay_chain[0]["receipt_id"] if replay_chain else None,
                "retry_outcome_receipt_id": next(
                    (entry["receipt_id"] for entry in replay_chain if entry["branch_class"] == "retry"),
                    None,
                ),
                "escalation_outcome_receipt_id": next(
                    (entry["receipt_id"] for entry in replay_chain if entry["branch_class"] == "escalation"),
                    None,
                ),
            },
            "observed_branches": [entry["branch_class"] for entry in replay_chain],
            "latest_receipt_id": replay_chain[-1]["receipt_id"] if replay_chain else None,
            "route_class": "internal_handoff",
            "payload_class": "runtime_report_bundle",
            "execution_mode": "governed_runtime",
            "branch_count": len(replay_chain),
            "trace_complete": True,
            "resolution_pending": True,
            "sealed": True,
        },
    }


def _entry(
    sequence: int,
    branch_class: str,
    artifact_type: str,
    receipt_id: str,
    outcome_status: str,
) -> dict:
    return {
        "sequence": sequence,
        "branch_class": branch_class,
        "artifact_type": artifact_type,
        "receipt_id": receipt_id,
        "occurred_at": f"2026-03-19T21:0{sequence}:00Z",
        "outcome_status": outcome_status,
        "route_class": "internal_handoff",
        "payload_class": "runtime_report_bundle",
        "execution_mode": "governed_runtime",
        "result_ref": f"{receipt_id}__RESULT",
        "source_receipt_ref": f"{receipt_id}__SOURCE",
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
    except CaseResolutionError:
        return {"case": case_name, "status": "passed"}
    except Exception as exc:
        return {"case": case_name, "status": "failed", "error": str(exc)}


def run_stage53_case_resolution_probe() -> dict:
    results = []

    def case_01_primary_success_resolution():
        resolution = build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5301",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="primary",
                        artifact_type="delivery_outcome_receipt",
                        receipt_id="WR-DELIVERY-OUTCOME-5301",
                        outcome_status="delivered",
                    )
                ],
            )
        )
        assert resolution["artifact_type"] == "case_resolution"
        assert resolution["payload"]["final_state"] == "success"
        assert resolution["payload"]["source_path"] == "primary"
        assert resolution["payload"]["actionable"] is True

    results.append(_expect_pass("case_01_primary_success_resolution", case_01_primary_success_resolution))

    def case_02_retry_resolved_resolution():
        resolution = build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5302",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="primary",
                        artifact_type="delivery_outcome_receipt",
                        receipt_id="WR-DELIVERY-OUTCOME-5302",
                        outcome_status="delivery_failed",
                    ),
                    _entry(
                        sequence=2,
                        branch_class="retry",
                        artifact_type="retry_outcome_receipt",
                        receipt_id="WR-RETRY-OUTCOME-5302",
                        outcome_status="retry_succeeded",
                    ),
                ],
            )
        )
        assert resolution["payload"]["final_state"] == "retry_resolved"
        assert resolution["payload"]["source_path"] == "retry"
        assert resolution["payload"]["authoritative_receipt_id"] == "WR-RETRY-OUTCOME-5302"

    results.append(_expect_pass("case_02_retry_resolved_resolution", case_02_retry_resolved_resolution))

    def case_03_escalated_resolution():
        resolution = build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5303",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="primary",
                        artifact_type="delivery_outcome_receipt",
                        receipt_id="WR-DELIVERY-OUTCOME-5303",
                        outcome_status="delivery_failed",
                    ),
                    _entry(
                        sequence=2,
                        branch_class="retry",
                        artifact_type="retry_outcome_receipt",
                        receipt_id="WR-RETRY-OUTCOME-5303",
                        outcome_status="retry_failed",
                    ),
                    _entry(
                        sequence=3,
                        branch_class="escalation",
                        artifact_type="escalation_outcome_receipt",
                        receipt_id="WR-ESCALATION-OUTCOME-5303",
                        outcome_status="escalation_completed",
                    ),
                ],
            )
        )
        assert resolution["payload"]["final_state"] == "escalated"
        assert resolution["payload"]["source_path"] == "escalation"
        assert resolution["payload"]["actionable"] is True

    results.append(_expect_pass("case_03_escalated_resolution", case_03_escalated_resolution))

    def case_04_terminal_failure_after_primary_failure():
        resolution = build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5304",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="primary",
                        artifact_type="delivery_outcome_receipt",
                        receipt_id="WR-DELIVERY-OUTCOME-5304",
                        outcome_status="delivery_failed",
                    )
                ],
            )
        )
        assert resolution["payload"]["final_state"] == "terminal_failure"
        assert resolution["payload"]["actionable"] is False
        assert resolution["payload"]["source_path"] == "primary"

    results.append(_expect_pass("case_04_terminal_failure_after_primary_failure", case_04_terminal_failure_after_primary_failure))

    def case_05_reject_invalid_artifact_type():
        build_case_resolution(
            {
                "artifact_type": "delivery_outcome_receipt",
                "payload": {},
            }
        )

    results.append(_expect_fail("case_05_reject_invalid_artifact_type", case_05_reject_invalid_artifact_type))

    def case_06_reject_empty_replay_chain():
        build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5306",
                replay_chain=[],
            )
        )

    results.append(_expect_fail("case_06_reject_empty_replay_chain", case_06_reject_empty_replay_chain))

    def case_07_reject_non_primary_start():
        build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5307",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="retry",
                        artifact_type="retry_outcome_receipt",
                        receipt_id="WR-RETRY-OUTCOME-5307",
                        outcome_status="retry_succeeded",
                    )
                ],
            )
        )

    results.append(_expect_fail("case_07_reject_non_primary_start", case_07_reject_non_primary_start))

    def case_08_reject_duplicate_branch_class():
        build_case_resolution(
            _audit_replay_index(
                case_id="WR-CASE-5308",
                replay_chain=[
                    _entry(
                        sequence=1,
                        branch_class="primary",
                        artifact_type="delivery_outcome_receipt",
                        receipt_id="WR-DELIVERY-OUTCOME-5308-A",
                        outcome_status="delivery_failed",
                    ),
                    _entry(
                        sequence=2,
                        branch_class="retry",
                        artifact_type="retry_outcome_receipt",
                        receipt_id="WR-RETRY-OUTCOME-5308-A",
                        outcome_status="retry_failed",
                    ),
                    _entry(
                        sequence=3,
                        branch_class="retry",
                        artifact_type="retry_outcome_receipt",
                        receipt_id="WR-RETRY-OUTCOME-5308-B",
                        outcome_status="retry_succeeded",
                    ),
                ],
            )
        )

    results.append(_expect_fail("case_08_reject_duplicate_branch_class", case_08_reject_duplicate_branch_class))

    def case_09_reject_unsealed_audit_replay_index():
        index = _audit_replay_index(
            case_id="WR-CASE-5309",
            replay_chain=[
                _entry(
                    sequence=1,
                    branch_class="primary",
                    artifact_type="delivery_outcome_receipt",
                    receipt_id="WR-DELIVERY-OUTCOME-5309",
                    outcome_status="delivered",
                )
            ],
        )
        index["payload"]["sealed"] = False
        build_case_resolution(index)

    results.append(_expect_fail("case_09_reject_unsealed_audit_replay_index", case_09_reject_unsealed_audit_replay_index))

    def case_10_reject_internal_field_leakage():
        index = _audit_replay_index(
            case_id="WR-CASE-5310",
            replay_chain=[
                _entry(
                    sequence=1,
                    branch_class="primary",
                    artifact_type="delivery_outcome_receipt",
                    receipt_id="WR-DELIVERY-OUTCOME-5310",
                    outcome_status="delivered",
                )
            ],
        )
        index["payload"]["_internal"] = {"unsafe": True}
        build_case_resolution(index)

    results.append(_expect_fail("case_10_reject_internal_field_leakage", case_10_reject_internal_field_leakage))

    passed = sum(1 for result in results if result["status"] == "passed")
    failed = sum(1 for result in results if result["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_stage53_case_resolution_probe())
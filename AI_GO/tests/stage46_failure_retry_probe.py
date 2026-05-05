from AI_GO.core.runtime.failure_retry.failure_retry_interface import (
    create_failure_retry_decision,
)


def run_probe():
    results = []

    valid_delivery_outcome_receipt = {
        "delivery_outcome_receipt_id": "DOR-TX-TE-ACK-001",
        "delivery_outcome_receipt_type": "delivery_outcome_receipt_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Transport envelope executed through manual release adapter.",
        "result": "executed",
        "transport_execution_ref": "TX-TE-ACK-001",
        "transport_execution_result_type": "transport_execution_result_v1",
        "transport_envelope_ref": "TE-ACK-001",
        "ack_index_ref": "ACK-001",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "adapter_class": "manual_release_adapter",
        "execution_attempted": True,
        "execution_permitted": True,
    }

    response = create_failure_retry_decision(valid_delivery_outcome_receipt)
    results.append(
        {
            "case": "case_01_valid_failure_retry_decision",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_delivery_outcome_receipt)
    del missing_field_payload["delivery_outcome_receipt_id"]
    response = create_failure_retry_decision(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_delivery_outcome_receipt)
    invalid_type_payload["delivery_outcome_receipt_type"] = "wrong_type"
    response = create_failure_retry_decision(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_delivery_outcome_receipt_type",
            "status": "passed"
            if response.get("reason") == "unapproved_delivery_outcome_receipt_type"
            else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = create_failure_retry_decision(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_delivery_outcome_receipt_payload",
            "status": "passed"
            if response.get("reason") == "invalid_delivery_outcome_receipt_payload"
            else "failed",
        }
    )

    leakage_payload = dict(valid_delivery_outcome_receipt)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = create_failure_retry_decision(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed"
            if response.get("reason") == "internal_field_leakage"
            else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_delivery_outcome_receipt)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = create_failure_retry_decision(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed"
            if response.get("reason") == "invalid_payload_class"
            else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_delivery_outcome_receipt)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = create_failure_retry_decision(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed"
            if response.get("reason") == "invalid_route_class"
            else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_delivery_outcome_receipt)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = create_failure_retry_decision(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed"
            if response.get("reason") == "invalid_execution_mode"
            else "failed",
        }
    )

    invalid_adapter_class_payload = dict(valid_delivery_outcome_receipt)
    invalid_adapter_class_payload["adapter_class"] = "unsafe_adapter"
    response = create_failure_retry_decision(invalid_adapter_class_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_adapter_class"
            else "failed",
        }
    )

    invalid_result_payload = dict(valid_delivery_outcome_receipt)
    invalid_result_payload["result"] = "mystery_state"
    response = create_failure_retry_decision(invalid_result_payload)
    results.append(
        {
            "case": "case_10_reject_invalid_outcome_result",
            "status": "passed"
            if response.get("reason") == "invalid_outcome_result"
            else "failed",
        }
    )

    failed_outcome_payload = dict(valid_delivery_outcome_receipt)
    failed_outcome_payload["result"] = "failed"
    response = create_failure_retry_decision(failed_outcome_payload)
    decision_ok = (
        response.get("status") == "ok"
        and response["failure_retry_decision"]["retry_eligible"] is True
        and response["failure_retry_decision"]["escalation_suggested"] is True
        and response["failure_retry_decision"]["terminal"] is False
    )
    results.append(
        {
            "case": "case_11_classify_failed_outcome_as_retryable_and_escalatable",
            "status": "passed" if decision_ok else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
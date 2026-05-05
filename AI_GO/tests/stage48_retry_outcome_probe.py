from AI_GO.core.runtime.retry_outcome.retry_outcome_interface import (
    create_retry_outcome_receipt,
)


def run_probe():
    results = []

    valid_retry_execution_result = {
        "retry_execution_id": "RTX-FRD-DOR-TX-TE-ACK-001",
        "retry_execution_result_type": "retry_execution_result_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Retry executed through manual retry adapter.",
        "result": "retried",
        "failure_retry_decision_ref": "FRD-DOR-TX-TE-ACK-001",
        "delivery_outcome_receipt_ref": "DOR-TX-TE-ACK-001",
        "transport_execution_ref": "TX-TE-ACK-001",
        "transport_envelope_ref": "TE-ACK-001",
        "ack_index_ref": "ACK-001",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "source_adapter_class": "manual_release_adapter",
        "retry_adapter_class": "manual_retry_adapter",
        "retry_attempted": True,
        "retry_permitted": True,
        "terminal": False,
        "retry_eligible": True,
        "escalation_suggested": True,
    }

    response = create_retry_outcome_receipt(valid_retry_execution_result)
    results.append(
        {
            "case": "case_01_valid_retry_outcome_receipt",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_retry_execution_result)
    del missing_field_payload["retry_execution_id"]
    response = create_retry_outcome_receipt(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_retry_execution_result)
    invalid_type_payload["retry_execution_result_type"] = "wrong_type"
    response = create_retry_outcome_receipt(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_retry_execution_result_type",
            "status": "passed"
            if response.get("reason") == "unapproved_retry_execution_result_type"
            else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = create_retry_outcome_receipt(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_retry_execution_result_payload",
            "status": "passed"
            if response.get("reason") == "invalid_retry_execution_result_payload"
            else "failed",
        }
    )

    leakage_payload = dict(valid_retry_execution_result)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = create_retry_outcome_receipt(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed"
            if response.get("reason") == "internal_field_leakage"
            else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_retry_execution_result)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = create_retry_outcome_receipt(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed"
            if response.get("reason") == "invalid_payload_class"
            else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_retry_execution_result)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = create_retry_outcome_receipt(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed"
            if response.get("reason") == "invalid_route_class"
            else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_retry_execution_result)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = create_retry_outcome_receipt(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed"
            if response.get("reason") == "invalid_execution_mode"
            else "failed",
        }
    )

    invalid_source_adapter_payload = dict(valid_retry_execution_result)
    invalid_source_adapter_payload["source_adapter_class"] = "unsafe_source_adapter"
    response = create_retry_outcome_receipt(invalid_source_adapter_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_source_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_source_adapter_class"
            else "failed",
        }
    )

    invalid_retry_adapter_payload = dict(valid_retry_execution_result)
    invalid_retry_adapter_payload["retry_adapter_class"] = "unsafe_retry_adapter"
    response = create_retry_outcome_receipt(invalid_retry_adapter_payload)
    results.append(
        {
            "case": "case_10_reject_invalid_retry_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_retry_adapter_class"
            else "failed",
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
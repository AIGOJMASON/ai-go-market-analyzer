from AI_GO.core.runtime.escalation_outcome.escalation_outcome_interface import (
    create_escalation_outcome_receipt,
)


def run_probe():
    results = []

    valid_escalation_execution_result = {
        "escalation_execution_id": "EEX-ED-001",
        "escalation_execution_result_type": "escalation_execution_result_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Escalation executed through operator queue escalation adapter.",
        "result": "escalated",
        "escalation_decision_ref": "ED-001",
        "source_receipt_ref": "DOR-001",
        "source_receipt_type": "delivery_outcome_receipt_v1",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "source_adapter_class": "manual_release_adapter",
        "retry_adapter_class": "none",
        "escalation_class": "operator_review",
        "escalation_route": "operator_queue",
        "escalation_adapter_class": "operator_queue_escalation_adapter",
        "escalation_attempted": True,
        "escalation_permitted": True,
    }

    response = create_escalation_outcome_receipt(valid_escalation_execution_result)
    results.append(
        {
            "case": "case_01_valid_escalation_outcome_receipt",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_escalation_execution_result)
    del missing_field_payload["escalation_execution_id"]
    response = create_escalation_outcome_receipt(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_escalation_execution_result)
    invalid_type_payload["escalation_execution_result_type"] = "wrong_type"
    response = create_escalation_outcome_receipt(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_escalation_execution_result_type",
            "status": "passed"
            if response.get("reason") == "unapproved_escalation_execution_result_type"
            else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = create_escalation_outcome_receipt(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_escalation_execution_result_payload",
            "status": "passed"
            if response.get("reason") == "invalid_escalation_execution_result_payload"
            else "failed",
        }
    )

    leakage_payload = dict(valid_escalation_execution_result)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = create_escalation_outcome_receipt(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed"
            if response.get("reason") == "internal_field_leakage"
            else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_escalation_execution_result)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = create_escalation_outcome_receipt(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed"
            if response.get("reason") == "invalid_payload_class"
            else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_escalation_execution_result)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = create_escalation_outcome_receipt(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed"
            if response.get("reason") == "invalid_route_class"
            else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_escalation_execution_result)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = create_escalation_outcome_receipt(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed"
            if response.get("reason") == "invalid_execution_mode"
            else "failed",
        }
    )

    invalid_source_adapter_payload = dict(valid_escalation_execution_result)
    invalid_source_adapter_payload["source_adapter_class"] = "unsafe_source_adapter"
    response = create_escalation_outcome_receipt(invalid_source_adapter_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_source_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_source_adapter_class"
            else "failed",
        }
    )

    invalid_retry_adapter_payload = dict(valid_escalation_execution_result)
    invalid_retry_adapter_payload["retry_adapter_class"] = "unsafe_retry_adapter"
    response = create_escalation_outcome_receipt(invalid_retry_adapter_payload)
    results.append(
        {
            "case": "case_10_reject_invalid_retry_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_retry_adapter_class"
            else "failed",
        }
    )

    invalid_escalation_adapter_payload = dict(valid_escalation_execution_result)
    invalid_escalation_adapter_payload["escalation_adapter_class"] = "unsafe_escalation_adapter"
    response = create_escalation_outcome_receipt(invalid_escalation_adapter_payload)
    results.append(
        {
            "case": "case_11_reject_invalid_escalation_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_escalation_adapter_class"
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
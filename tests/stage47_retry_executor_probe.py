from AI_GO.core.runtime.retry_executor.retry_executor_interface import (
    execute_retry_decision,
)


def run_probe():
    results = []

    valid_failure_retry_decision = {
        "failure_retry_decision_id": "FRD-DOR-TX-TE-ACK-001",
        "failure_retry_decision_type": "failure_retry_decision_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Execution failed. Retry may be permitted and escalation is suggested.",
        "result": "failed",
        "delivery_outcome_receipt_ref": "DOR-TX-TE-ACK-001",
        "transport_execution_ref": "TX-TE-ACK-001",
        "transport_envelope_ref": "TE-ACK-001",
        "ack_index_ref": "ACK-001",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "adapter_class": "manual_release_adapter",
        "execution_attempted": True,
        "execution_permitted": True,
        "terminal": False,
        "retry_eligible": True,
        "escalation_suggested": True,
    }

    response = execute_retry_decision(valid_failure_retry_decision)
    results.append(
        {
            "case": "case_01_valid_retry_execution",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_failure_retry_decision)
    del missing_field_payload["failure_retry_decision_id"]
    response = execute_retry_decision(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_failure_retry_decision)
    invalid_type_payload["failure_retry_decision_type"] = "wrong_type"
    response = execute_retry_decision(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_failure_retry_decision_type",
            "status": "passed"
            if response.get("reason") == "unapproved_failure_retry_decision_type"
            else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = execute_retry_decision(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_failure_retry_decision_payload",
            "status": "passed"
            if response.get("reason") == "invalid_failure_retry_decision_payload"
            else "failed",
        }
    )

    leakage_payload = dict(valid_failure_retry_decision)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = execute_retry_decision(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed"
            if response.get("reason") == "internal_field_leakage"
            else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_failure_retry_decision)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = execute_retry_decision(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed"
            if response.get("reason") == "invalid_payload_class"
            else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_failure_retry_decision)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = execute_retry_decision(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed"
            if response.get("reason") == "invalid_route_class"
            else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_failure_retry_decision)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = execute_retry_decision(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed"
            if response.get("reason") == "invalid_execution_mode"
            else "failed",
        }
    )

    invalid_adapter_class_payload = dict(valid_failure_retry_decision)
    invalid_adapter_class_payload["adapter_class"] = "unsafe_adapter"
    response = execute_retry_decision(invalid_adapter_class_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_adapter_class"
            else "failed",
        }
    )

    denied_retry_payload = dict(valid_failure_retry_decision)
    denied_retry_payload["retry_eligible"] = False
    response = execute_retry_decision(denied_retry_payload)
    denied_ok = (
        response.get("status") == "ok"
        and response["retry_execution_result"]["result"] == "retry_denied"
        and response["retry_execution_result"]["retry_attempted"] is False
        and response["retry_execution_result"]["retry_permitted"] is False
    )
    results.append(
        {
            "case": "case_10_deny_retry_when_not_retry_eligible",
            "status": "passed" if denied_ok else "failed",
        }
    )

    terminal_payload = dict(valid_failure_retry_decision)
    terminal_payload["terminal"] = True
    response = execute_retry_decision(terminal_payload)
    terminal_ok = (
        response.get("status") == "ok"
        and response["retry_execution_result"]["result"] == "retry_denied"
        and response["retry_execution_result"]["retry_attempted"] is False
    )
    results.append(
        {
            "case": "case_11_deny_retry_when_terminal",
            "status": "passed" if terminal_ok else "failed",
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
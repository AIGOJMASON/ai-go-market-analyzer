from AI_GO.core.runtime.escalation_executor.escalation_executor_interface import (
    execute_escalation_decision,
)


def run_probe():
    results = []

    valid_escalation_decision = {
        "escalation_decision_id": "ED-DOR-001",
        "escalation_decision_type": "escalation_decision_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Delivery outcome failed. Escalation to operator review is required.",
        "result": "failed",
        "source_receipt_ref": "DOR-001",
        "source_receipt_type": "delivery_outcome_receipt_v1",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "source_adapter_class": "manual_release_adapter",
        "retry_adapter_class": "none",
        "escalation_required": True,
        "escalation_class": "operator_review",
        "escalation_route": "operator_queue",
    }

    response = execute_escalation_decision(valid_escalation_decision)
    results.append(
        {
            "case": "case_01_valid_escalation_execution",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_escalation_decision)
    del missing_field_payload["escalation_decision_id"]
    response = execute_escalation_decision(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_escalation_decision)
    invalid_type_payload["escalation_decision_type"] = "wrong_type"
    response = execute_escalation_decision(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_escalation_decision_type",
            "status": "passed"
            if response.get("reason") == "unapproved_escalation_decision_type"
            else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = execute_escalation_decision(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_escalation_decision_payload",
            "status": "passed"
            if response.get("reason") == "invalid_escalation_decision_payload"
            else "failed",
        }
    )

    leakage_payload = dict(valid_escalation_decision)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = execute_escalation_decision(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed"
            if response.get("reason") == "internal_field_leakage"
            else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_escalation_decision)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = execute_escalation_decision(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed"
            if response.get("reason") == "invalid_payload_class"
            else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_escalation_decision)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = execute_escalation_decision(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed"
            if response.get("reason") == "invalid_route_class"
            else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_escalation_decision)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = execute_escalation_decision(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed"
            if response.get("reason") == "invalid_execution_mode"
            else "failed",
        }
    )

    invalid_source_adapter_payload = dict(valid_escalation_decision)
    invalid_source_adapter_payload["source_adapter_class"] = "unsafe_source_adapter"
    response = execute_escalation_decision(invalid_source_adapter_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_source_adapter_class",
            "status": "passed"
            if response.get("reason") == "invalid_source_adapter_class"
            else "failed",
        }
    )

    denied_payload = dict(valid_escalation_decision)
    denied_payload["escalation_required"] = False
    response = execute_escalation_decision(denied_payload)
    denied_ok = (
        response.get("status") == "ok"
        and response["escalation_execution_result"]["result"] == "escalation_denied"
        and response["escalation_execution_result"]["escalation_attempted"] is False
        and response["escalation_execution_result"]["escalation_permitted"] is False
    )
    results.append(
        {
            "case": "case_10_deny_escalation_when_not_required",
            "status": "passed" if denied_ok else "failed",
        }
    )

    invalid_retry_adapter_payload = dict(valid_escalation_decision)
    invalid_retry_adapter_payload["retry_adapter_class"] = "unsafe_retry_adapter"
    response = execute_escalation_decision(invalid_retry_adapter_payload)
    results.append(
        {
            "case": "case_11_reject_invalid_retry_adapter_class",
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
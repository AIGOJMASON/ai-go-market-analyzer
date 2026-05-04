from AI_GO.core.runtime.escalation_decision.escalation_decision_interface import (
    create_escalation_decision,
)


def run_probe():
    results = []

    valid_delivery_outcome_receipt = {
        "delivery_outcome_receipt_id": "DOR-TX-001",
        "delivery_outcome_receipt_type": "delivery_outcome_receipt_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Transport execution failed.",
        "result": "failed",
        "transport_execution_ref": "TX-001",
        "transport_execution_result_type": "transport_execution_result_v1",
        "transport_envelope_ref": "TE-001",
        "ack_index_ref": "ACK-001",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "adapter_class": "manual_release_adapter",
        "execution_attempted": True,
        "execution_permitted": True,
    }

    valid_retry_outcome_receipt = {
        "retry_outcome_receipt_id": "ROR-RTX-001",
        "retry_outcome_receipt_type": "retry_outcome_receipt_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Retry was denied.",
        "result": "retry_denied",
        "retry_execution_ref": "RTX-001",
        "retry_execution_result_type": "retry_execution_result_v1",
        "failure_retry_decision_ref": "FRD-001",
        "delivery_outcome_receipt_ref": "DOR-TX-001",
        "transport_execution_ref": "TX-001",
        "transport_envelope_ref": "TE-001",
        "ack_index_ref": "ACK-001",
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "source_adapter_class": "manual_release_adapter",
        "retry_adapter_class": "manual_retry_adapter",
        "retry_attempted": False,
        "retry_permitted": False,
        "terminal": True,
        "retry_eligible": False,
        "escalation_suggested": True,
    }

    response = create_escalation_decision(valid_delivery_outcome_receipt)
    delivery_ok = (
        response.get("status") == "ok"
        and response["escalation_decision"]["escalation_required"] is True
        and response["escalation_decision"]["escalation_class"] == "operator_review"
    )
    results.append(
        {
            "case": "case_01_valid_delivery_outcome_escalation_decision",
            "status": "passed" if delivery_ok else "failed",
        }
    )

    response = create_escalation_decision(valid_retry_outcome_receipt)
    retry_ok = (
        response.get("status") == "ok"
        and response["escalation_decision"]["escalation_required"] is True
        and response["escalation_decision"]["escalation_class"] == "policy_block"
    )
    results.append(
        {
            "case": "case_02_valid_retry_outcome_escalation_decision",
            "status": "passed" if retry_ok else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = create_escalation_decision(malformed_payload)
    results.append(
        {
            "case": "case_03_reject_invalid_source_receipt_payload",
            "status": "passed" if response.get("reason") == "invalid_source_receipt_payload" else "failed",
        }
    )

    leakage_payload = dict(valid_delivery_outcome_receipt)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = create_escalation_decision(leakage_payload)
    results.append(
        {
            "case": "case_04_reject_internal_field_leakage",
            "status": "passed" if response.get("reason") == "internal_field_leakage" else "failed",
        }
    )

    invalid_type_payload = {
        "unknown_receipt_type": "wrong_type",
        "result": "failed",
    }
    response = create_escalation_decision(invalid_type_payload)
    results.append(
        {
            "case": "case_05_reject_unapproved_source_receipt_type",
            "status": "passed" if response.get("reason") == "unapproved_source_receipt_type" else "failed",
        }
    )

    missing_field_payload = dict(valid_delivery_outcome_receipt)
    del missing_field_payload["delivery_outcome_receipt_id"]
    response = create_escalation_decision(missing_field_payload)
    results.append(
        {
            "case": "case_06_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_delivery_outcome_receipt)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = create_escalation_decision(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_payload_class",
            "status": "passed" if response.get("reason") == "invalid_payload_class" else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_retry_outcome_receipt)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = create_escalation_decision(invalid_route_class_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_route_class",
            "status": "passed" if response.get("reason") == "invalid_route_class" else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_retry_outcome_receipt)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = create_escalation_decision(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_09_reject_invalid_execution_mode",
            "status": "passed" if response.get("reason") == "invalid_execution_mode" else "failed",
        }
    )

    invalid_source_adapter_payload = dict(valid_delivery_outcome_receipt)
    invalid_source_adapter_payload["adapter_class"] = "unsafe_source_adapter"
    response = create_escalation_decision(invalid_source_adapter_payload)
    results.append(
        {
            "case": "case_10_reject_invalid_source_adapter_class",
            "status": "passed" if response.get("reason") == "invalid_source_adapter_class" else "failed",
        }
    )

    invalid_retry_adapter_payload = dict(valid_retry_outcome_receipt)
    invalid_retry_adapter_payload["retry_adapter_class"] = "unsafe_retry_adapter"
    response = create_escalation_decision(invalid_retry_adapter_payload)
    results.append(
        {
            "case": "case_11_reject_invalid_retry_adapter_class",
            "status": "passed" if response.get("reason") == "invalid_retry_adapter_class" else "failed",
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
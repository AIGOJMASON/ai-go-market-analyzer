from AI_GO.core.runtime.transport_executor.transport_executor_interface import (
    execute_transport_envelope,
)


def run_probe():
    results = []

    valid_transport_envelope = {
        "transport_envelope_id": "TE-ACK-001",
        "transport_envelope_type": "delivery_transport_envelope_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Transport envelope ready for execution.",
        "result": "accepted",
        "ack_index_ref": "ACK-001",
        "ack_index_type": "runtime_acknowledgement_index_v1",
        "delivery_receipt_ref": "DR-001",
        "delivery_index_ref": "DI-001",
        "dispatch_manifest_ref": "DM-001",
        "bundle_ref": "BND-001",
        "report_count": 3,
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
        "transport_permitted": True,
    }

    response = execute_transport_envelope(valid_transport_envelope)
    results.append(
        {
            "case": "case_01_valid_transport_execution",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_transport_envelope)
    del missing_field_payload["transport_envelope_id"]
    response = execute_transport_envelope(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_type_payload = dict(valid_transport_envelope)
    invalid_type_payload["transport_envelope_type"] = "wrong_type"
    response = execute_transport_envelope(invalid_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_transport_envelope_type",
            "status": "passed" if response.get("reason") == "unapproved_transport_envelope_type" else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = execute_transport_envelope(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_transport_envelope_payload",
            "status": "passed" if response.get("reason") == "invalid_transport_envelope_payload" else "failed",
        }
    )

    leakage_payload = dict(valid_transport_envelope)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = execute_transport_envelope(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed" if response.get("reason") == "internal_field_leakage" else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_transport_envelope)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = execute_transport_envelope(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed" if response.get("reason") == "invalid_payload_class" else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_transport_envelope)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = execute_transport_envelope(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed" if response.get("reason") == "invalid_route_class" else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_transport_envelope)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = execute_transport_envelope(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed" if response.get("reason") == "invalid_execution_mode" else "failed",
        }
    )

    denied_payload = dict(valid_transport_envelope)
    denied_payload["transport_permitted"] = False
    response = execute_transport_envelope(denied_payload)
    denied_ok = (
        response.get("status") == "ok"
        and response["transport_execution_result"]["result"] == "denied"
        and response["transport_execution_result"]["execution_attempted"] is False
    )
    results.append(
        {
            "case": "case_09_deny_execution_when_transport_not_permitted",
            "status": "passed" if denied_ok else "failed",
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
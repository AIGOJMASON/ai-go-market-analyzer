from AI_GO.core.runtime.delivery_transport.delivery_transport_interface import (
    create_delivery_transport_envelope,
)


def run_probe():
    results = []

    valid_ack_index = {
        "ack_index_id": "ACK-001",
        "ack_index_type": "runtime_acknowledgement_index_v1",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Downstream acknowledgement registered.",
        "result": "accepted",
        "acknowledgement_registered": True,
        "delivery_receipt_ref": "DR-001",
        "delivery_index_ref": "DI-001",
        "dispatch_manifest_ref": "DM-001",
        "bundle_ref": "BND-001",
        "report_count": 3,
        "payload_class": "runtime_report_bundle",
        "route_class": "internal_handoff",
        "execution_mode": "manual_release",
    }

    response = create_delivery_transport_envelope(valid_ack_index)
    results.append(
        {
            "case": "case_01_valid_delivery_transport_envelope",
            "status": "passed" if response.get("status") == "ok" else "failed",
        }
    )

    missing_field_payload = dict(valid_ack_index)
    del missing_field_payload["ack_index_id"]
    response = create_delivery_transport_envelope(missing_field_payload)
    results.append(
        {
            "case": "case_02_reject_missing_required_field",
            "status": "passed" if response.get("status") == "rejected" else "failed",
        }
    )

    invalid_ack_type_payload = dict(valid_ack_index)
    invalid_ack_type_payload["ack_index_type"] = "wrong_type"
    response = create_delivery_transport_envelope(invalid_ack_type_payload)
    results.append(
        {
            "case": "case_03_reject_unapproved_ack_index_type",
            "status": "passed" if response.get("reason") == "unapproved_ack_index_type" else "failed",
        }
    )

    malformed_payload = "not_a_dict"
    response = create_delivery_transport_envelope(malformed_payload)
    results.append(
        {
            "case": "case_04_reject_invalid_ack_index_payload",
            "status": "passed" if response.get("reason") == "invalid_ack_index_payload" else "failed",
        }
    )

    leakage_payload = dict(valid_ack_index)
    leakage_payload["_debug_trace"] = {"leak": True}
    response = create_delivery_transport_envelope(leakage_payload)
    results.append(
        {
            "case": "case_05_reject_internal_field_leakage",
            "status": "passed" if response.get("reason") == "internal_field_leakage" else "failed",
        }
    )

    invalid_payload_class_payload = dict(valid_ack_index)
    invalid_payload_class_payload["payload_class"] = "invalid_payload"
    response = create_delivery_transport_envelope(invalid_payload_class_payload)
    results.append(
        {
            "case": "case_06_reject_invalid_payload_class",
            "status": "passed" if response.get("reason") == "invalid_payload_class" else "failed",
        }
    )

    invalid_route_class_payload = dict(valid_ack_index)
    invalid_route_class_payload["route_class"] = "invalid_route"
    response = create_delivery_transport_envelope(invalid_route_class_payload)
    results.append(
        {
            "case": "case_07_reject_invalid_route_class",
            "status": "passed" if response.get("reason") == "invalid_route_class" else "failed",
        }
    )

    invalid_execution_mode_payload = dict(valid_ack_index)
    invalid_execution_mode_payload["execution_mode"] = "unsafe_mode"
    response = create_delivery_transport_envelope(invalid_execution_mode_payload)
    results.append(
        {
            "case": "case_08_reject_invalid_execution_mode",
            "status": "passed" if response.get("reason") == "invalid_execution_mode" else "failed",
        }
    )

    gated_payload = dict(valid_ack_index)
    gated_payload["acknowledgement_registered"] = False
    response = create_delivery_transport_envelope(gated_payload)
    permitted = (
        response.get("status") == "ok"
        and response["transport_envelope"]["transport_permitted"] is False
    )
    results.append(
        {
            "case": "case_09_transport_permission_gating",
            "status": "passed" if permitted else "failed",
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
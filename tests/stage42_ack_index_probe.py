from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.ack_index.ack_index_interface import (
    get_ack_index_view,
    validate_ack_index_payload,
    validate_ack_index_type,
)


def _valid_delivery_receipt_payload():
    return {
        "delivery_receipt_id": "RECEIPT-1001",
        "delivery_receipt_type": "runtime_delivery_receipt",
        "timestamp": "2026-03-19T08:00:00Z",
        "summary": "Runtime delivery receipt confirms downstream acceptance.",
        "result": "accepted",
        "delivery_index_ref": "DELIVERY-1001",
        "delivery_index_type": "runtime_delivery_index",
        "dispatch_manifest_ref": "DISPATCH-1001",
        "manifest_ref": "MANIFEST-1001",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "accepted": True,
        "internal_note": "must not leak",
    }


def _valid_ack_index_payload():
    return {
        "ack_index_id": "ACK-0001",
        "ack_index_type": "runtime_ack_index",
        "timestamp": "2026-03-19T08:10:00Z",
        "summary": "Runtime acknowledgement index is registry-complete.",
        "result": "accepted",
        "delivery_receipt_ref": "RECEIPT-1001",
        "delivery_receipt_type": "runtime_delivery_receipt",
        "delivery_index_ref": "DELIVERY-1001",
        "dispatch_manifest_ref": "DISPATCH-1001",
        "manifest_ref": "MANIFEST-1001",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "acceptance_registered": True,
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_ack_index_payload()
    del payload["summary"]
    return payload


def _invalid_ack_index_type():
    payload = _valid_ack_index_payload()
    payload["ack_index_type"] = "raw_ack_dump"
    return payload


def _invalid_delivery_receipt_type():
    payload = _valid_ack_index_payload()
    payload["delivery_receipt_type"] = "raw_delivery_receipt"
    return payload


def _invalid_delivery_receipt_payload():
    return {
        "delivery_receipt_id": "RECEIPT-9999",
        "timestamp": "2026-03-19T08:20:00Z",
        "summary": "Incomplete delivery receipt.",
        "result": "unknown",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_ack_index",
            _valid_ack_index_payload(),
            _valid_delivery_receipt_payload(),
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            _valid_delivery_receipt_payload(),
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_ack_index_type",
            _invalid_ack_index_type(),
            _valid_delivery_receipt_payload(),
            "fail_type",
        ),
        (
            "case_04_reject_unapproved_delivery_receipt_type",
            _invalid_delivery_receipt_type(),
            _valid_delivery_receipt_payload(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_delivery_receipt_payload",
            _valid_ack_index_payload(),
            _invalid_delivery_receipt_payload(),
            "fail_delivery_receipt",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_ack_index_payload(),
            _valid_delivery_receipt_payload(),
            "check_redaction",
        ),
    ]

    for case_name, payload, delivery_receipt_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_ack_index_view(payload, delivery_receipt_payload)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped ack index",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_ack_index_payload(payload)
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "ack index payload unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_ack_index_type(payload["ack_index_type"])
                if type_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid ack index type unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_delivery_receipt":
                try:
                    get_ack_index_view(payload, delivery_receipt_payload)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid delivery receipt payload unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_ack_index_view(payload, delivery_receipt_payload)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into ack index",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

        except Exception as exc:
            results.append(
                {
                    "case": case_name,
                    "status": "failed",
                    "reason": f"unexpected exception: {exc}",
                }
            )
            failed += 1

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    pprint(run_probe())
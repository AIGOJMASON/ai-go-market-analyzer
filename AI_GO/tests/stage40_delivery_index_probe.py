from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.delivery_index.delivery_index_interface import (
    get_delivery_index_view,
    validate_delivery_index_payload,
    validate_delivery_index_type,
)


def _valid_dispatch_manifest_payload():
    return {
        "dispatch_manifest_id": "DISPATCH-1001",
        "dispatch_manifest_type": "runtime_dispatch_manifest",
        "timestamp": "2026-03-19T06:00:00Z",
        "summary": "Runtime dispatch manifest ready for downstream delivery.",
        "result": "ready",
        "export_index_ref": "EXPORT-1001",
        "export_index_type": "runtime_export_index",
        "manifest_ref": "MANIFEST-1001",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "delivery_ready": True,
        "internal_note": "must not leak",
    }


def _valid_delivery_index_payload():
    return {
        "delivery_index_id": "DELIVERY-0001",
        "delivery_index_type": "runtime_delivery_index",
        "timestamp": "2026-03-19T06:10:00Z",
        "summary": "Runtime delivery index is registry-complete for downstream handoff.",
        "result": "ready",
        "dispatch_manifest_ref": "DISPATCH-1001",
        "dispatch_manifest_type": "runtime_dispatch_manifest",
        "export_index_ref": "EXPORT-1001",
        "manifest_ref": "MANIFEST-1001",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "registry_complete": True,
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_delivery_index_payload()
    del payload["summary"]
    return payload


def _invalid_delivery_index_type():
    payload = _valid_delivery_index_payload()
    payload["delivery_index_type"] = "raw_delivery_dump"
    return payload


def _invalid_dispatch_manifest_type():
    payload = _valid_delivery_index_payload()
    payload["dispatch_manifest_type"] = "raw_dispatch_manifest"
    return payload


def _invalid_dispatch_manifest_payload():
    return {
        "dispatch_manifest_id": "DISPATCH-9999",
        "timestamp": "2026-03-19T06:20:00Z",
        "summary": "Incomplete dispatch manifest.",
        "result": "unknown",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_delivery_index",
            _valid_delivery_index_payload(),
            _valid_dispatch_manifest_payload(),
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            _valid_dispatch_manifest_payload(),
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_delivery_index_type",
            _invalid_delivery_index_type(),
            _valid_dispatch_manifest_payload(),
            "fail_type",
        ),
        (
            "case_04_reject_unapproved_dispatch_manifest_type",
            _invalid_dispatch_manifest_type(),
            _valid_dispatch_manifest_payload(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_dispatch_manifest_payload",
            _valid_delivery_index_payload(),
            _invalid_dispatch_manifest_payload(),
            "fail_dispatch_manifest",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_delivery_index_payload(),
            _valid_dispatch_manifest_payload(),
            "check_redaction",
        ),
    ]

    for case_name, payload, dispatch_manifest_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_delivery_index_view(payload, dispatch_manifest_payload)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped delivery index",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_delivery_index_payload(payload)
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "delivery index payload unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_delivery_index_type(payload["delivery_index_type"])
                if type_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid delivery index type unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_dispatch_manifest":
                try:
                    get_delivery_index_view(payload, dispatch_manifest_payload)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid dispatch manifest payload unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_delivery_index_view(payload, dispatch_manifest_payload)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into delivery index",
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
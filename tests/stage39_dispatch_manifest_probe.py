from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.dispatch_manifest.dispatch_manifest_interface import (
    get_dispatch_manifest_view,
    validate_dispatch_manifest_payload,
    validate_dispatch_manifest_type,
)


def _valid_export_index_payload():
    return {
        "export_index_id": "EXPORT-1001",
        "export_index_type": "runtime_export_index",
        "timestamp": "2026-03-19T05:00:00Z",
        "summary": "Runtime export index ready for dispatch preparation.",
        "result": "ready",
        "manifest_ref": "MANIFEST-1001",
        "manifest_type": "runtime_bundle_manifest",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "dispatch_ready": True,
        "internal_note": "must not leak",
    }


def _valid_dispatch_manifest_payload():
    return {
        "dispatch_manifest_id": "DISPATCH-0001",
        "dispatch_manifest_type": "runtime_dispatch_manifest",
        "timestamp": "2026-03-19T05:10:00Z",
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


def _missing_required_field():
    payload = _valid_dispatch_manifest_payload()
    del payload["summary"]
    return payload


def _invalid_dispatch_manifest_type():
    payload = _valid_dispatch_manifest_payload()
    payload["dispatch_manifest_type"] = "raw_dispatch_dump"
    return payload


def _invalid_export_index_type():
    payload = _valid_dispatch_manifest_payload()
    payload["export_index_type"] = "raw_export_index"
    return payload


def _invalid_export_index_payload():
    return {
        "export_index_id": "EXPORT-9999",
        "timestamp": "2026-03-19T05:20:00Z",
        "summary": "Incomplete export index.",
        "result": "unknown",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_dispatch_manifest",
            _valid_dispatch_manifest_payload(),
            _valid_export_index_payload(),
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            _valid_export_index_payload(),
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_dispatch_manifest_type",
            _invalid_dispatch_manifest_type(),
            _valid_export_index_payload(),
            "fail_type",
        ),
        (
            "case_04_reject_unapproved_export_index_type",
            _invalid_export_index_type(),
            _valid_export_index_payload(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_export_index_payload",
            _valid_dispatch_manifest_payload(),
            _invalid_export_index_payload(),
            "fail_export_index",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_dispatch_manifest_payload(),
            _valid_export_index_payload(),
            "check_redaction",
        ),
    ]

    for case_name, payload, export_index_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_dispatch_manifest_view(payload, export_index_payload)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped dispatch manifest",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_dispatch_manifest_payload(payload)
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "dispatch manifest payload unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_dispatch_manifest_type(
                    payload["dispatch_manifest_type"]
                )
                if type_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid dispatch manifest type unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_export_index":
                try:
                    get_dispatch_manifest_view(payload, export_index_payload)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid export index payload unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_dispatch_manifest_view(payload, export_index_payload)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into dispatch manifest",
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
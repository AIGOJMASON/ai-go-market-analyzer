from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.bundle_manifest.bundle_manifest_interface import (
    get_bundle_manifest_view,
    validate_manifest_payload,
    validate_manifest_type,
)


def _valid_bundle_payload():
    return {
        "bundle_id": "BUNDLE-1001",
        "bundle_type": "runtime_report_bundle",
        "timestamp": "2026-03-19T03:00:00Z",
        "summary": "Governed runtime report bundle ready.",
        "result": "ready",
        "report_refs": [
            "REPORT-1001",
            "REPORT-1002",
            "REPORT-1003",
        ],
        "report_count": 3,
        "internal_note": "must not leak",
    }


def _valid_manifest_payload():
    return {
        "manifest_id": "MANIFEST-0001",
        "manifest_type": "runtime_bundle_manifest",
        "timestamp": "2026-03-19T03:10:00Z",
        "summary": "Bundle manifest ready for downstream handoff.",
        "result": "ready",
        "bundle_ref": "BUNDLE-1001",
        "bundle_type": "runtime_report_bundle",
        "report_count": 3,
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_manifest_payload()
    del payload["summary"]
    return payload


def _invalid_manifest_type():
    payload = _valid_manifest_payload()
    payload["manifest_type"] = "raw_manifest_dump"
    return payload


def _invalid_bundle_type():
    payload = _valid_manifest_payload()
    payload["bundle_type"] = "raw_bundle_dump"
    return payload


def _invalid_bundle_payload():
    return {
        "bundle_id": "BUNDLE-9999",
        "timestamp": "2026-03-19T03:20:00Z",
        "summary": "Incomplete bundle.",
        "result": "unknown",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_bundle_manifest",
            _valid_manifest_payload(),
            _valid_bundle_payload(),
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            _valid_bundle_payload(),
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_manifest_type",
            _invalid_manifest_type(),
            _valid_bundle_payload(),
            "fail_type",
        ),
        (
            "case_04_reject_unapproved_bundle_type",
            _invalid_bundle_type(),
            _valid_bundle_payload(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_bundle_payload",
            _valid_manifest_payload(),
            _invalid_bundle_payload(),
            "fail_bundle",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_manifest_payload(),
            _valid_bundle_payload(),
            "check_redaction",
        ),
    ]

    for case_name, payload, bundle_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_bundle_manifest_view(payload, bundle_payload)
                if not shaped:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "empty shaped manifest",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_manifest_payload(payload)
                if validation_result["ok"]:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "manifest payload unexpectedly validated",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_manifest_type(payload["manifest_type"])
                if type_result["ok"]:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "invalid manifest type unexpectedly validated",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_bundle":
                try:
                    get_bundle_manifest_view(payload, bundle_payload)
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "invalid bundle payload unexpectedly accepted",
                    })
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_bundle_manifest_view(payload, bundle_payload)
                if "internal_note" in shaped:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "internal field leaked into manifest",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

        except Exception as exc:
            results.append({
                "case": case_name,
                "status": "failed",
                "reason": f"unexpected exception: {exc}",
            })
            failed += 1

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    pprint(run_probe())
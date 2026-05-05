from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.export_index.export_index_interface import (
    get_export_index_view,
    validate_export_index_payload,
    validate_export_index_type,
)


def _valid_manifest_payload():
    return {
        "manifest_id": "MANIFEST-1001",
        "manifest_type": "runtime_bundle_manifest",
        "timestamp": "2026-03-19T04:00:00Z",
        "summary": "Bundle manifest ready for downstream handoff.",
        "result": "ready",
        "bundle_ref": "BUNDLE-1001",
        "bundle_type": "runtime_report_bundle",
        "report_count": 3,
        "internal_note": "must not leak",
    }


def _valid_export_index_payload():
    return {
        "export_index_id": "EXPORT-0001",
        "export_index_type": "runtime_export_index",
        "timestamp": "2026-03-19T04:10:00Z",
        "summary": "Runtime export index ready for dispatch preparation.",
        "result": "ready",
        "manifest_ref": "MANIFEST-1001",
        "manifest_type": "runtime_bundle_manifest",
        "bundle_ref": "BUNDLE-1001",
        "report_count": 3,
        "dispatch_ready": True,
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_export_index_payload()
    del payload["summary"]
    return payload


def _invalid_export_index_type():
    payload = _valid_export_index_payload()
    payload["export_index_type"] = "raw_export_dump"
    return payload


def _invalid_manifest_type():
    payload = _valid_export_index_payload()
    payload["manifest_type"] = "raw_manifest_dump"
    return payload


def _invalid_manifest_payload():
    return {
        "manifest_id": "MANIFEST-9999",
        "timestamp": "2026-03-19T04:20:00Z",
        "summary": "Incomplete manifest.",
        "result": "unknown",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_export_index",
            _valid_export_index_payload(),
            _valid_manifest_payload(),
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            _valid_manifest_payload(),
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_export_index_type",
            _invalid_export_index_type(),
            _valid_manifest_payload(),
            "fail_type",
        ),
        (
            "case_04_reject_unapproved_manifest_type",
            _invalid_manifest_type(),
            _valid_manifest_payload(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_manifest_payload",
            _valid_export_index_payload(),
            _invalid_manifest_payload(),
            "fail_manifest",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_export_index_payload(),
            _valid_manifest_payload(),
            "check_redaction",
        ),
    ]

    for case_name, payload, manifest_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_export_index_view(payload, manifest_payload)
                if not shaped:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "empty shaped export index",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_export_index_payload(payload)
                if validation_result["ok"]:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "export index payload unexpectedly validated",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_export_index_type(payload["export_index_type"])
                if type_result["ok"]:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "invalid export index type unexpectedly validated",
                    })
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_manifest":
                try:
                    get_export_index_view(payload, manifest_payload)
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "invalid manifest payload unexpectedly accepted",
                    })
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_export_index_view(payload, manifest_payload)
                if "internal_note" in shaped:
                    results.append({
                        "case": case_name,
                        "status": "failed",
                        "reason": "internal field leaked into export index",
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
from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.report_bundle.report_bundle_interface import (
    get_report_bundle_view,
    validate_bundle_payload,
    validate_bundle_type,
)


def _status_report():
    return {
        "report_id": "REPORT-1001",
        "report_type": "status_report",
        "timestamp": "2026-03-19T02:00:00Z",
        "summary": "Runtime ready.",
        "result": "ready",
        "internal_note": "must not leak",
    }


def _operator_summary_report():
    return {
        "report_id": "REPORT-1002",
        "report_type": "operator_summary_report",
        "timestamp": "2026-03-19T02:01:00Z",
        "summary": "Runtime operational.",
        "result": "operational",
        "internal_note": "must not leak",
    }


def _runtime_brief_report():
    return {
        "report_id": "REPORT-1003",
        "report_type": "runtime_brief_report",
        "timestamp": "2026-03-19T02:02:00Z",
        "summary": "Runtime surfaces ready.",
        "result": "ready",
        "rendered_block": "[operator_summary_view]\\nsummary: Runtime surfaces are ready.",
        "internal_note": "must not leak",
    }


def _valid_bundle_payload():
    return {
        "bundle_id": "BUNDLE-0001",
        "bundle_type": "runtime_report_bundle",
        "timestamp": "2026-03-19T02:10:00Z",
        "summary": "Governed runtime report bundle ready for downstream use.",
        "result": "ready",
        "report_refs": [
            "REPORT-1001",
            "REPORT-1002",
            "REPORT-1003",
        ],
        "report_count": 3,
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_bundle_payload()
    del payload["summary"]
    return payload


def _invalid_bundle_type():
    payload = _valid_bundle_payload()
    payload["bundle_type"] = "raw_report_dump"
    return payload


def _invalid_report_payload():
    return {
        "report_id": "REPORT-9999",
        "timestamp": "2026-03-19T02:20:00Z",
        "summary": "Incomplete report.",
        "result": "unknown",
    }


def _unapproved_report_type():
    return {
        "report_id": "REPORT-8888",
        "report_type": "raw_internal_report",
        "timestamp": "2026-03-19T02:21:00Z",
        "summary": "Should not be allowed.",
        "result": "blocked",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    valid_reports = [
        _status_report(),
        _operator_summary_report(),
        _runtime_brief_report(),
    ]

    cases = [
        (
            "case_01_valid_runtime_report_bundle",
            _valid_bundle_payload(),
            valid_reports,
            "pass",
        ),
        (
            "case_02_reject_missing_required_field",
            _missing_required_field(),
            valid_reports,
            "fail_payload",
        ),
        (
            "case_03_reject_invalid_bundle_type",
            _invalid_bundle_type(),
            valid_reports,
            "fail_type",
        ),
        (
            "case_04_reject_invalid_report_payload",
            _valid_bundle_payload(),
            [_invalid_report_payload()],
            "fail_reports",
        ),
        (
            "case_05_reject_unapproved_report_type",
            _valid_bundle_payload(),
            [_unapproved_report_type()],
            "fail_reports",
        ),
        (
            "case_06_reject_internal_field_leakage",
            _valid_bundle_payload(),
            valid_reports,
            "check_redaction",
        ),
    ]

    for case_name, payload, report_payloads, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_report_bundle_view(payload, report_payloads)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped bundle",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_bundle_payload(payload)
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "bundle payload unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_bundle_type(payload["bundle_type"])
                if type_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid bundle type unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_reports":
                try:
                    get_report_bundle_view(payload, report_payloads)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid report payloads unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_report_bundle_view(payload, report_payloads)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into bundle",
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
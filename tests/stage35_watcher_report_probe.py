from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.watcher_report.watcher_report_interface import (
    get_watcher_report_view,
    validate_report_payload,
    validate_report_type,
)


def _status_source():
    return {
        "status_id": "STATUS-3001",
        "status_class": "runtime_readiness",
        "timestamp": "2026-03-19T01:00:00Z",
        "summary": "Runtime is ready.",
        "result": "ready",
        "internal_note": "must not leak",
    }


def _summary_source():
    return {
        "summary_id": "SUMMARY-3001",
        "summary_class": "runtime_overview",
        "timestamp": "2026-03-19T01:01:00Z",
        "summary": "Runtime is operational.",
        "result": "operational",
        "internal_note": "must not leak",
    }


def _runtime_brief_source():
    return {
        "rendered_block": "[operator_summary_view]\nsummary: Runtime surfaces are ready.",
        "summary": "Runtime surfaces are ready.",
        "timestamp": "2026-03-19T01:02:00Z",
        "internal_note": "must not leak",
    }


def _valid_status_report():
    return {
        "report_id": "REPORT-0001",
        "report_type": "status_report",
        "timestamp": "2026-03-19T01:10:00Z",
        "summary": "Watcher status report: runtime ready.",
        "result": "ready",
        "internal_note": "must not leak",
    }


def _valid_operator_summary_report():
    return {
        "report_id": "REPORT-0002",
        "report_type": "operator_summary_report",
        "timestamp": "2026-03-19T01:11:00Z",
        "summary": "Watcher operator summary report: runtime operational.",
        "result": "operational",
        "internal_note": "must not leak",
    }


def _valid_runtime_brief_report():
    return {
        "report_id": "REPORT-0003",
        "report_type": "runtime_brief_report",
        "timestamp": "2026-03-19T01:12:00Z",
        "summary": "Watcher runtime brief report.",
        "result": "ready",
        "rendered_block": "[operator_summary_view]\nsummary: Runtime surfaces are ready.",
        "internal_note": "must not leak",
    }


def _missing_required_field():
    payload = _valid_status_report()
    del payload["summary"]
    return payload


def _invalid_report_type():
    payload = _valid_status_report()
    payload["report_type"] = "raw_dump_report"
    return payload


def _invalid_source_for_report():
    return {
        "summary": "incomplete source",
        "timestamp": "2026-03-19T01:13:00Z",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        ("case_01_valid_status_report", _valid_status_report(), _status_source(), "pass"),
        (
            "case_02_valid_operator_summary_report",
            _valid_operator_summary_report(),
            _summary_source(),
            "pass",
        ),
        (
            "case_03_valid_runtime_brief_report",
            _valid_runtime_brief_report(),
            _runtime_brief_source(),
            "pass",
        ),
        (
            "case_04_reject_missing_required_field",
            _missing_required_field(),
            _status_source(),
            "fail_payload",
        ),
        (
            "case_05_reject_invalid_report_type",
            _invalid_report_type(),
            _status_source(),
            "fail_type",
        ),
        (
            "case_06_reject_invalid_source_payload",
            _valid_status_report(),
            _invalid_source_for_report(),
            "fail_source",
        ),
        (
            "case_07_reject_internal_field_leakage_status_report",
            _valid_status_report(),
            _status_source(),
            "check_redaction",
        ),
        (
            "case_08_reject_internal_field_leakage_runtime_brief_report",
            _valid_runtime_brief_report(),
            _runtime_brief_source(),
            "check_redaction",
        ),
    ]

    for case_name, payload, source_payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_watcher_report_view(payload, source_payload)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped watcher report",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_report_payload(payload)
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "payload unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_type":
                type_result = validate_report_type(payload["report_type"])
                if type_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid report type unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_source":
                try:
                    get_watcher_report_view(payload, source_payload)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid source payload unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_watcher_report_view(payload, source_payload)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into watcher report",
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
from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.operator.operator_summary_interface import (
    get_operator_summary_view,
    validate_operator_summary_payload,
    validate_summary_class,
)


def _runtime_readiness_source():
    return {
        "status_id": "STATUS-1001",
        "status_class": "runtime_readiness",
        "timestamp": "2026-03-18T23:00:00Z",
        "summary": "Runtime is ready.",
        "result": "ready",
    }


def _stage_completion_source():
    return {
        "status_id": "STATUS-1002",
        "status_class": "stage_completion",
        "timestamp": "2026-03-18T23:01:00Z",
        "summary": "Stage 32 closed successfully.",
        "stage": 32,
        "result": "complete",
    }


def _probe_health_source():
    return {
        "status_id": "STATUS-1003",
        "status_class": "probe_health",
        "timestamp": "2026-03-18T23:02:00Z",
        "summary": "Stage 32 probe passed.",
        "probe_ref": "stage32_runtime_status_probe",
        "result": "passed",
    }


def _output_health_source():
    return {
        "status_id": "STATUS-1004",
        "status_class": "output_health",
        "timestamp": "2026-03-18T23:03:00Z",
        "summary": "Stage 30 output boundary is healthy.",
        "stage": 30,
        "probe_ref": "stage30_output_boundary_probe",
        "result": "healthy",
    }


def _consumption_health_source():
    return {
        "status_id": "STATUS-1005",
        "status_class": "consumption_health",
        "timestamp": "2026-03-18T23:04:00Z",
        "summary": "Stage 31 consumption boundary is healthy.",
        "stage": 31,
        "probe_ref": "stage31_output_consumption_probe",
        "result": "healthy",
    }


def _valid_runtime_overview():
    return {
        "summary_id": "SUMMARY-0001",
        "summary_class": "runtime_overview",
        "timestamp": "2026-03-18T23:10:00Z",
        "summary": "Runtime is operational and governed.",
        "result": "operational",
        "internal_note": "must not leak",
    }


def _valid_stage_overview():
    return {
        "summary_id": "SUMMARY-0002",
        "summary_class": "stage_overview",
        "timestamp": "2026-03-18T23:11:00Z",
        "summary": "Latest closed stage is Stage 32.",
        "stage": 32,
        "result": "complete",
    }


def _valid_probe_overview():
    return {
        "summary_id": "SUMMARY-0003",
        "summary_class": "probe_overview",
        "timestamp": "2026-03-18T23:12:00Z",
        "summary": "Recent probes are passing.",
        "probe_refs": [
            "stage30_output_boundary_probe",
            "stage31_output_consumption_probe",
            "stage32_runtime_status_probe",
        ],
        "result": "passing",
    }


def _valid_surface_readiness():
    return {
        "summary_id": "SUMMARY-0004",
        "summary_class": "surface_readiness",
        "timestamp": "2026-03-18T23:13:00Z",
        "summary": "Output, consumption, and runtime reporting surfaces are ready.",
        "surface_refs": [
            "output_boundary",
            "output_consumption",
            "runtime_status",
        ],
        "result": "ready",
    }


def _missing_required_field():
    payload = _valid_runtime_overview()
    del payload["summary"]
    return payload


def _invalid_summary_class():
    payload = _valid_runtime_overview()
    payload["summary_class"] = "raw_operator_dump"
    return payload


def _invalid_source_for_summary():
    return [_probe_health_source()]


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        (
            "case_01_valid_runtime_overview_summary",
            _valid_runtime_overview(),
            [_runtime_readiness_source()],
            "pass",
        ),
        (
            "case_02_valid_stage_overview_summary",
            _valid_stage_overview(),
            [_stage_completion_source()],
            "pass",
        ),
        (
            "case_03_valid_probe_overview_summary",
            _valid_probe_overview(),
            [_probe_health_source()],
            "pass",
        ),
        (
            "case_04_valid_surface_readiness_summary",
            _valid_surface_readiness(),
            [_output_health_source(), _consumption_health_source(), _runtime_readiness_source()],
            "pass",
        ),
        (
            "case_05_reject_missing_required_field",
            _missing_required_field(),
            [_runtime_readiness_source()],
            "fail_payload",
        ),
        (
            "case_06_reject_invalid_summary_class",
            _invalid_summary_class(),
            [_runtime_readiness_source()],
            "fail_class",
        ),
        (
            "case_07_reject_unapproved_source_status_class",
            _valid_runtime_overview(),
            _invalid_source_for_summary(),
            "fail_source",
        ),
        (
            "case_08_reject_internal_field_leakage",
            _valid_runtime_overview(),
            [_runtime_readiness_source()],
            "check_redaction",
        ),
    ]

    for case_name, payload, source_payloads, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_operator_summary_view(payload, source_payloads)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped operator summary",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_operator_summary_payload(payload)
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

            elif expected_mode == "fail_class":
                class_result = validate_summary_class(payload["summary_class"])
                if class_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid summary class unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_source":
                try:
                    get_operator_summary_view(payload, source_payloads)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "unapproved source payload unexpectedly accepted",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_operator_summary_view(payload, source_payloads)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into operator summary",
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
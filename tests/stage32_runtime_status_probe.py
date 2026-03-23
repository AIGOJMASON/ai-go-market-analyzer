from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.status.status_interface import (
    get_status_view,
    validate_status_class,
    validate_status_payload,
)


def _valid_runtime_readiness():
    return {
        "status_id": "STATUS-0001",
        "status_class": "runtime_readiness",
        "timestamp": "2026-03-18T22:00:00Z",
        "summary": "Runtime is ready and bounded status reporting is available.",
        "result": "ready",
        "internal_note": "should not appear in shaped view",
    }


def _valid_stage_completion():
    return {
        "status_id": "STATUS-0002",
        "status_class": "stage_completion",
        "timestamp": "2026-03-18T22:01:00Z",
        "summary": "Stage 31 closed successfully.",
        "stage": 31,
        "result": "complete",
    }


def _valid_probe_health():
    return {
        "status_id": "STATUS-0003",
        "status_class": "probe_health",
        "timestamp": "2026-03-18T22:02:00Z",
        "summary": "Stage 31 probe passed with no failures.",
        "probe_ref": "stage31_output_consumption_probe",
        "result": "passed",
    }


def _missing_required_field():
    payload = _valid_runtime_readiness()
    del payload["summary"]
    return payload


def _invalid_status_class():
    payload = _valid_runtime_readiness()
    payload["status_class"] = "raw_dump"
    return payload


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        ("case_01_valid_runtime_readiness_status", _valid_runtime_readiness(), "pass"),
        ("case_02_valid_stage_completion_status", _valid_stage_completion(), "pass"),
        ("case_03_valid_probe_health_status", _valid_probe_health(), "pass"),
        ("case_04_reject_missing_required_field", _missing_required_field(), "fail_payload"),
        ("case_05_reject_invalid_status_class", _invalid_status_class(), "fail_class"),
        ("case_06_reject_internal_field_leakage", _valid_runtime_readiness(), "check_redaction"),
    ]

    for case_name, payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = get_status_view(payload)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "empty shaped status view",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_payload":
                validation_result = validate_status_payload(payload)
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
                class_result = validate_status_class(payload["status_class"])
                if class_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "invalid status class unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_status_view(payload)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked into status view",
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
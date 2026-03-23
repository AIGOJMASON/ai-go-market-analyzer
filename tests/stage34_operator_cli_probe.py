from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.operator_cli.cli_presenter import (
    render_cli_block,
    shape_cli_payload,
    validate_cli_view,
)


def _valid_status_view():
    return {
        "status_id": "STATUS-2001",
        "status_class": "probe_health",
        "timestamp": "2026-03-19T00:00:00Z",
        "summary": "Stage 33 probe passed.",
        "probe_ref": "stage33_operator_summary_probe",
        "result": "passed",
        "internal_note": "must not leak",
    }


def _valid_operator_summary_view():
    return {
        "summary_id": "SUMMARY-2001",
        "summary_class": "surface_readiness",
        "timestamp": "2026-03-19T00:01:00Z",
        "summary": "Runtime surfaces are ready for operator use.",
        "surface_refs": [
            "output_boundary",
            "output_consumption",
            "runtime_status",
            "operator_summary",
        ],
        "result": "ready",
        "internal_note": "must not leak",
    }


def run_probe():
    results = []
    passed = 0
    failed = 0

    cases = [
        ("case_01_valid_status_cli_view", "status_view", _valid_status_view(), "pass"),
        ("case_02_valid_operator_summary_cli_view", "operator_summary_view", _valid_operator_summary_view(), "pass"),
        ("case_03_reject_unknown_cli_view", "unknown_view", _valid_status_view(), "fail_view"),
        ("case_04_reject_internal_field_leakage_status", "status_view", _valid_status_view(), "check_redaction"),
        ("case_05_reject_internal_field_leakage_summary", "operator_summary_view", _valid_operator_summary_view(), "check_redaction"),
        ("case_06_render_status_cli_block", "status_view", _valid_status_view(), "check_render"),
        ("case_07_render_summary_cli_block", "operator_summary_view", _valid_operator_summary_view(), "check_render"),
    ]

    for case_name, view_type, payload, expected_mode in cases:
        try:
            if expected_mode == "pass":
                shaped = shape_cli_payload(view_type, payload)
                if not shaped:
                    results.append({"case": case_name, "status": "failed", "reason": "empty shaped cli payload"})
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_view":
                view_result = validate_cli_view(view_type)
                if view_result["ok"]:
                    results.append({"case": case_name, "status": "failed", "reason": "unknown cli view unexpectedly validated"})
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = shape_cli_payload(view_type, payload)
                if "internal_note" in shaped:
                    results.append({"case": case_name, "status": "failed", "reason": "internal field leaked into cli payload"})
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_render":
                rendered = render_cli_block(view_type, payload)
                if not rendered or "internal_note" in rendered:
                    results.append({"case": case_name, "status": "failed", "reason": "rendered output invalid or leaked internal field"})
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

        except Exception as exc:
            results.append({"case": case_name, "status": "failed", "reason": f"unexpected exception: {exc}"})
            failed += 1

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    pprint(run_probe())
from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.output.consumer_interface import (
    get_consumer_view,
    validate_consumer,
)


def _valid_closed_artifact():
    return {
        "artifact_id": "ART-DECISION-0001",
        "artifact_type": "decision_packet",
        "originating_core": "STRATEGY_LAYER",
        "validation_receipt_ref": "RECEIPT-DECISION-0001",
        "lifecycle_state": "CLOSED",
        "timestamp": "2026-03-18T21:00:00Z",
        "summary": "Closed decision packet approved for runtime output consumption.",
        "internal_note": "should never leave policy boundary",
    }


def _open_artifact():
    artifact = _valid_closed_artifact()
    artifact["lifecycle_state"] = "OPEN"
    return artifact


def run_probe():
    results = []
    passed = 0
    failed = 0

    artifact = _valid_closed_artifact()

    cases = [
        ("case_01_valid_watcher_summary_shape", "watcher", artifact, "pass"),
        ("case_02_valid_cli_summary_with_refs", "cli", artifact, "pass"),
        ("case_03_valid_audit_surface_closed_artifact_shape", "audit_surface", artifact, "pass"),
        ("case_04_reject_unknown_consumer", "unknown_surface", artifact, "fail_consumer"),
        ("case_05_reject_open_artifact_even_for_valid_consumer", "watcher", _open_artifact(), "fail_output"),
        ("case_06_reject_internal_field_leakage_to_watcher", "watcher", artifact, "check_redaction"),
    ]

    for case_name, consumer_name, case_artifact, expected_mode in cases:
        try:
            if expected_mode == "fail_consumer":
                consumer_result = validate_consumer(consumer_name)
                if consumer_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "unknown consumer unexpectedly validated",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_output":
                try:
                    get_consumer_view(case_artifact, consumer_name)
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "open artifact unexpectedly exposed",
                        }
                    )
                    failed += 1
                except ValueError:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "check_redaction":
                shaped = get_consumer_view(case_artifact, consumer_name)
                if "internal_note" in shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "internal field leaked to watcher",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "pass":
                shaped = get_consumer_view(case_artifact, consumer_name)
                if not shaped:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "consumer received empty shaped artifact",
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
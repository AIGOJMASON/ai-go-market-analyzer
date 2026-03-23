from __future__ import annotations

from pprint import pprint

from AI_GO.core.runtime.output.watcher_interface import (
    expose_to_watcher,
    validate_output,
)


def _closed_valid_planning_brief():
    return {
        "artifact_id": "ART-PLANNING-0001",
        "artifact_type": "planning_brief",
        "originating_core": "PM_CORE",
        "validation_receipt_ref": "RECEIPT-0001",
        "lifecycle_state": "CLOSED",
        "timestamp": "2026-03-18T20:00:00Z",
        "summary": "Validated planning brief for watcher exposure.",
    }


def _open_artifact():
    artifact = _closed_valid_planning_brief()
    artifact["lifecycle_state"] = "OPEN"
    return artifact


def _missing_receipt():
    artifact = _closed_valid_planning_brief()
    artifact["validation_receipt_ref"] = ""
    return artifact


def _missing_field():
    artifact = _closed_valid_planning_brief()
    del artifact["summary"]
    return artifact


def _disallowed_artifact_type():
    artifact = _closed_valid_planning_brief()
    artifact["artifact_type"] = "raw_packet"
    return artifact


def run_probe():
    results = []

    cases = [
        ("case_01_valid_closed_planning_brief", _closed_valid_planning_brief(), "pass"),
        ("case_02_reject_open_artifact", _open_artifact(), "fail_validation"),
        ("case_03_reject_missing_receipt", _missing_receipt(), "fail_validation"),
        ("case_04_reject_missing_required_field", _missing_field(), "fail_validation"),
        ("case_05_reject_disallowed_artifact_type", _disallowed_artifact_type(), "fail_exposure"),
    ]

    passed = 0
    failed = 0

    for case_name, artifact, expected_mode in cases:
        try:
            validation_result = validate_output(artifact)

            if expected_mode == "pass":
                exposed = expose_to_watcher(artifact)
                assert exposed == artifact
                results.append({"case": case_name, "status": "passed"})
                passed += 1

            elif expected_mode == "fail_validation":
                if validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "validation unexpectedly passed",
                        }
                    )
                    failed += 1
                else:
                    results.append({"case": case_name, "status": "passed"})
                    passed += 1

            elif expected_mode == "fail_exposure":
                if not validation_result["ok"]:
                    results.append(
                        {
                            "case": case_name,
                            "status": "failed",
                            "reason": "validation failed before exposure gate",
                        }
                    )
                    failed += 1
                else:
                    try:
                        expose_to_watcher(artifact)
                        results.append(
                            {
                                "case": case_name,
                                "status": "failed",
                                "reason": "disallowed artifact was exposed",
                            }
                        )
                        failed += 1
                    except ValueError:
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
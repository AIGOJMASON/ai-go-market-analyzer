# AI_GO/tests/stage_market_analyzer_v1_pre_interface_smi_probe.py

from __future__ import annotations

from api.pre_interface_smi import record_pre_interface_continuity


def _build_passed_watcher_receipt():
    return {
        "validation_id": "watcher_market_analyzer_v1_20260330T163500Z_probe",
        "watcher_status": "passed",
    }


def _build_failed_watcher_receipt():
    return {
        "validation_id": "watcher_market_analyzer_v1_20260330T163500Z_probe_fail",
        "watcher_status": "failed",
    }


def _build_system_view():
    return {
        "case_panel": {
            "case_id": "probe-case-001"
        },
        "runtime_panel": {
            "event_theme": "energy_rebound"
        },
        "recommendation_panel": {
            "items": [
                {
                    "symbol": "XLE"
                }
            ]
        }
    }


def run_probe():
    passed_result = record_pre_interface_continuity(
        watcher_receipt=_build_passed_watcher_receipt(),
        system_view=_build_system_view(),
        core_id="market_analyzer_v1",
    )

    failed_result = record_pre_interface_continuity(
        watcher_receipt=_build_failed_watcher_receipt(),
        system_view=_build_system_view(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_passed_watcher_records_continuity",
        "status": "passed" if passed_result.get("status") == "recorded" else "failed",
    })

    results.append({
        "case": "case_02_failed_watcher_rejected",
        "status": "passed" if failed_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_continuity_key_present",
        "status": "passed" if passed_result.get("continuity_key") else "failed",
    })

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())
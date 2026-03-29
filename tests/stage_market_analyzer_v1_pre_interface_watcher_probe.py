# AI_GO/tests/stage_market_analyzer_v1_pre_interface_watcher_probe.py

from __future__ import annotations

from AI_GO.api.pre_interface_watcher import build_pre_interface_watcher_receipt


def _valid_payload():
    return {
        "status": "ok",
        "request_id": "probe-001",
        "core_id": "market_analyzer_v1",
        "mode": "advisory",
        "execution_allowed": False,
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "case_panel": {
            "case_id": "probe-001",
            "title": "Probe case",
        },
        "governance_panel": {
            "watcher_passed": True,
            "approval_required": True,
        },
        "recommendation_panel": {
            "count": 1,
            "items": [
                {
                    "symbol": "XLE",
                    "confidence": "medium",
                }
            ],
        },
        "refinement_panel": {
            "signal": "pattern_detected",
        },
        "external_memory_panel": {
            "promotion_status": "promoted",
        },
    }


def main():
    passed = 0
    failed = 0
    results = []

    receipt = build_pre_interface_watcher_receipt(_valid_payload())
    if receipt["status"] == "passed":
        passed += 1
        results.append({"case": "case_01_valid_payload_passes", "status": "passed"})
    else:
        failed += 1
        results.append({"case": "case_01_valid_payload_passes", "status": "failed", "detail": receipt})

    broken = _valid_payload()
    broken["execution_allowed"] = True
    receipt = build_pre_interface_watcher_receipt(broken)
    if receipt["status"] == "failed" and "execution_allowed_must_be_false" in receipt["failures"]:
        passed += 1
        results.append({"case": "case_02_execution_allowed_rejected", "status": "passed"})
    else:
        failed += 1
        results.append({"case": "case_02_execution_allowed_rejected", "status": "failed", "detail": receipt})

    leaking = _valid_payload()
    leaking["internal_state"] = {"unsafe": True}
    receipt = build_pre_interface_watcher_receipt(leaking)
    if receipt["status"] == "failed" and any(item.startswith("forbidden_key_present") for item in receipt["failures"]):
        passed += 1
        results.append({"case": "case_03_internal_leakage_rejected", "status": "passed"})
    else:
        failed += 1
        results.append({"case": "case_03_internal_leakage_rejected", "status": "failed", "detail": receipt})

    print(
        {
            "passed": passed,
            "failed": failed,
            "results": results,
        }
    )


if __name__ == "__main__":
    main()
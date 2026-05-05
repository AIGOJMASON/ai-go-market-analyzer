from __future__ import annotations

from AI_GO.api.closeout import build_closeout_artifact


def _build_receipt_payload():
    return {
        "receipt_id": "rcpt_market_analyzer_v1_20260331T235959Z_probe",
        "core_id": "market_analyzer_v1",
        "execution_allowed": False,
        "approval_required": True,
    }


def _build_watcher_receipt():
    return {
        "validation_id": "watcher_market_analyzer_v1_20260331T235959Z_probe",
        "watcher_status": "passed",
        "issues": [],
    }


def _build_system_view():
    return {
        "case_panel": {
            "case_id": "probe-case-001",
            "title": "Live market event",
            "symbol": "XLE",
        },
        "runtime_panel": {
            "market_regime": "normal",
            "event_theme": "energy_rebound",
            "macro_bias": "neutral",
            "headline": "Energy rebound after necessity shock",
        },
        "recommendation_panel": {
            "items": [
                {
                    "symbol": "XLE",
                    "entry": 100.0,
                    "exit": 108.0,
                    "thesis": "Rebound continuation",
                    "state": "present",
                }
            ]
        },
    }


def run_probe():
    artifact = build_closeout_artifact(
        receipt_payload=_build_receipt_payload(),
        watcher_receipt=_build_watcher_receipt(),
        system_view=_build_system_view(),
    )

    results = []

    results.append({
        "case": "case_01_runtime_event_theme_preserved",
        "status": "passed"
        if artifact.get("runtime_panel", {}).get("event_theme") == "energy_rebound"
        else "failed",
    })

    results.append({
        "case": "case_02_recommendation_symbol_preserved",
        "status": "passed"
        if artifact.get("recommendation_panel", {}).get("items", [{}])[0].get("symbol") == "XLE"
        else "failed",
    })

    results.append({
        "case": "case_03_recommendation_entry_preserved",
        "status": "passed"
        if artifact.get("recommendation_panel", {}).get("items", [{}])[0].get("entry") == 100.0
        else "failed",
    })

    results.append({
        "case": "case_04_expected_behavior_derived",
        "status": "passed"
        if artifact.get("expected_behavior") == "energy rebound"
        else "failed",
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
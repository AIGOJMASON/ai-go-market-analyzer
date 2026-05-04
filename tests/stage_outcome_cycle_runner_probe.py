from __future__ import annotations

from AI_GO.core.outcome_feedback.outcome_cycle_runner import run_outcome_cycle


def _build_closeout_loader():
    def _loader():
        return [
            {
                "closeout_id": "closeout_market_analyzer_v1_20260401T010000Z_probe_old",
                "closeout_status": "accepted",
                "runtime_panel": {
                    "event_theme": "energy_rebound"
                },
                "recommendation_panel": {
                    "items": [
                        {
                            "symbol": "XLE",
                            "entry": 100.0
                        }
                    ]
                }
            },
            {
                "closeout_id": "closeout_market_analyzer_v1_20260401T010500Z_probe_latest",
                "closeout_status": "accepted",
                "runtime_panel": {
                    "event_theme": "energy_rebound"
                },
                "recommendation_panel": {
                    "items": [
                        {
                            "symbol": "XLE",
                            "entry": 100.0
                        }
                    ]
                }
            }
        ]

    return _loader


def _build_fetcher():
    def _fetcher(symbol: str):
        return {
            "symbol": symbol,
            "price": 105.0,
            "observed_at": "2026-04-01T01:06:00Z",
            "source": "market_feed",
        }

    return _fetcher


def run_probe():
    result = run_outcome_cycle(
        core_id="market_analyzer_v1",
        closeout_loader=_build_closeout_loader(),
        fetcher=_build_fetcher(),
    )

    results = []

    results.append({
        "case": "case_01_cycle_processes_one_eligible_closeout",
        "status": "passed"
        if result.get("result", {}).get("status") == "ingested"
        else "failed",
    })

    results.append({
        "case": "case_02_latest_closeout_selected",
        "status": "passed"
        if result.get("closeout_id") == "closeout_market_analyzer_v1_20260401T010500Z_probe_latest"
        else "failed",
    })

    results.append({
        "case": "case_03_outcome_class_present",
        "status": "passed"
        if result.get("result", {}).get("outcome_class") == "confirmed"
        else "failed",
    })

    results.append({
        "case": "case_04_receipt_path_present",
        "status": "passed"
        if result.get("receipt_path")
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
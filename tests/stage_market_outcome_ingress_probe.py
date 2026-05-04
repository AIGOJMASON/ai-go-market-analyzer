from __future__ import annotations

from AI_GO.api.market_outcome_ingress import ingest_market_outcome_result


def _build_closeout_artifact():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260401T003500Z_probe",
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


def _build_missing_reference_closeout_artifact():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260401T003500Z_probe_missing_ref",
        "closeout_status": "accepted",
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


def _build_fetcher_success():
    def _fetcher(symbol: str):
        return {
            "symbol": symbol,
            "price": 105.0,
            "observed_at": "2026-04-01T00:36:00Z",
            "source": "market_feed",
        }

    return _fetcher


def run_probe():
    success_result = ingest_market_outcome_result(
        closeout_artifact=_build_closeout_artifact(),
        core_id="market_analyzer_v1",
        fetcher=_build_fetcher_success(),
    )

    missing_reference_result = ingest_market_outcome_result(
        closeout_artifact=_build_missing_reference_closeout_artifact(),
        core_id="market_analyzer_v1",
        fetcher=_build_fetcher_success(),
    )

    results = []

    results.append({
        "case": "case_01_valid_market_quote_records_outcome_feedback",
        "status": "passed" if success_result.get("status") == "ingested" else "failed",
    })

    results.append({
        "case": "case_02_missing_reference_price_rejected",
        "status": "passed" if missing_reference_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_confirmed_outcome_class_returned",
        "status": "passed" if success_result.get("outcome_class") == "confirmed" else "failed",
    })

    results.append({
        "case": "case_04_market_delta_present",
        "status": "passed" if success_result.get("delta_pct") == 5.0 else "failed",
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
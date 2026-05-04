from __future__ import annotations

from AI_GO.api.outcome_ingress import ingest_outcome_result
from AI_GO.api.outcome_ingress_schema import build_outcome_ingress_request


def _build_closeout_artifact():
    return {
        "closeout_id": "closeout_market_analyzer_v1_20260401T001500Z_probe",
        "closeout_status": "accepted",
        "runtime_panel": {
            "event_theme": "energy_rebound",
        },
    }


def _build_valid_request():
    return build_outcome_ingress_request(
        closeout_id="closeout_market_analyzer_v1_20260401T001500Z_probe",
        actual_outcome="confirmed energy rebound after follow-through buying",
        source="market_feed",
        notes="Outcome captured from bounded feed input",
        observed_at="2026-04-01T00:16:00Z",
    )


def _build_mismatched_request():
    return build_outcome_ingress_request(
        closeout_id="closeout_market_analyzer_v1_mismatch_probe",
        actual_outcome="confirmed energy rebound after follow-through buying",
        source="market_feed",
    )


def run_probe():
    valid_result = ingest_outcome_result(
        request_payload=_build_valid_request(),
        closeout_artifact=_build_closeout_artifact(),
        core_id="market_analyzer_v1",
    )

    mismatched_result = ingest_outcome_result(
        request_payload=_build_mismatched_request(),
        closeout_artifact=_build_closeout_artifact(),
        core_id="market_analyzer_v1",
    )

    results = []

    results.append({
        "case": "case_01_valid_outcome_ingress_records_outcome_feedback",
        "status": "passed" if valid_result.get("status") == "ingested" else "failed",
    })

    results.append({
        "case": "case_02_closeout_id_mismatch_rejected",
        "status": "passed" if mismatched_result.get("status") == "rejected" else "failed",
    })

    results.append({
        "case": "case_03_outcome_class_present",
        "status": "passed" if valid_result.get("outcome_class") else "failed",
    })

    results.append({
        "case": "case_04_index_written",
        "status": "passed" if valid_result.get("index_status") == "indexed" else "failed",
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
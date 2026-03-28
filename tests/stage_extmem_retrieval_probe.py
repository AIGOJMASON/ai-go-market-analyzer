from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
    run_market_analyzer_external_memory_retrieval,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
    run_market_analyzer_external_memory_path,
)


def _seed_records() -> None:
    run_market_analyzer_external_memory_path(
        request_id="seed-extmem-001",
        symbol="XLE",
        headline="Confirmed energy disruption event",
        price_change_pct=2.4,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_rebound",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="live_market_input",
    )
    run_market_analyzer_external_memory_path(
        request_id="seed-extmem-002",
        symbol="XOM",
        headline="Confirmed energy operator update",
        price_change_pct=1.4,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_update",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="official_filing",
    )
    run_market_analyzer_external_memory_path(
        request_id="seed-extmem-003",
        symbol="TSLA",
        headline="Unconfirmed social rumor spikes speculative chatter",
        price_change_pct=0.8,
        sector="consumer",
        confirmation="unconfirmed",
        event_theme="speculative_move",
        macro_bias="mixed",
        route_mode="pm_route",
        source_type="social_scrape",
    )


def case_01_retrieval_returns_bounded_market_records() -> dict:
    _seed_records()
    result = run_market_analyzer_external_memory_retrieval(
        limit=10,
        requester_profile="market_analyzer_reader",
    )

    artifact = result["artifact"]
    receipt = result["receipt"]

    passed = (
        result["status"] == "ok"
        and artifact is not None
        and artifact["artifact_type"] == "external_memory_retrieval_artifact"
        and receipt["artifact_type"] == "external_memory_retrieval_receipt"
        and artifact["returned_count"] >= 1
        and len(artifact["records"]) <= 10
    )
    return {
        "case": "case_01_retrieval_returns_bounded_market_records",
        "status": "passed" if passed else "failed",
        "details": {
            "returned_count": artifact["returned_count"] if artifact else None,
            "matched_count": artifact["matched_count"] if artifact else None,
            "receipt_type": receipt["artifact_type"],
        },
    }


def case_02_retrieval_filters_by_symbol() -> dict:
    _seed_records()
    result = run_market_analyzer_external_memory_retrieval(
        limit=10,
        requester_profile="market_analyzer_reader",
        symbol="XLE",
    )

    artifact = result["artifact"]
    records = artifact["records"] if artifact else []
    all_xle = all(
        record["payload_summary"].get("symbol") == "XLE"
        for record in records
    )

    passed = (
        result["status"] == "ok"
        and artifact is not None
        and artifact["returned_count"] >= 1
        and all_xle
    )
    return {
        "case": "case_02_retrieval_filters_by_symbol",
        "status": "passed" if passed else "failed",
        "details": {
            "returned_count": artifact["returned_count"] if artifact else None,
            "all_xle": all_xle,
        },
    }


def case_03_retrieval_rejects_excessive_limit() -> dict:
    result = run_market_analyzer_external_memory_retrieval(
        limit=100,
        requester_profile="market_analyzer_reader",
    )

    receipt = result["receipt"]
    passed = (
        result["status"] == "failed"
        and receipt["artifact_type"] == "external_memory_retrieval_failure_receipt"
        and receipt["failure_reason"] == "limit_exceeds_profile_max"
    )
    return {
        "case": "case_03_retrieval_rejects_excessive_limit",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "receipt_type": receipt["artifact_type"],
            "failure_reason": receipt["failure_reason"],
        },
    }


def case_04_retrieval_rejects_invalid_profile() -> dict:
    result = run_market_analyzer_external_memory_retrieval(
        limit=5,
        requester_profile="unknown_reader",
    )

    receipt = result["receipt"]
    passed = (
        result["status"] == "failed"
        and receipt["artifact_type"] == "external_memory_retrieval_failure_receipt"
        and receipt["failure_reason"] == "invalid_requester_profile"
    )
    return {
        "case": "case_04_retrieval_rejects_invalid_profile",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": receipt["failure_reason"],
        },
    }


def run_probe() -> dict:
    cases = [
        case_01_retrieval_returns_bounded_market_records(),
        case_02_retrieval_filters_by_symbol(),
        case_03_retrieval_rejects_excessive_limit(),
        case_04_retrieval_rejects_invalid_profile(),
    ]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())
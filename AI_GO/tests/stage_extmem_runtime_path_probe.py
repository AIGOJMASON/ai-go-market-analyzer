from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
    run_market_analyzer_external_memory_path,
)


def case_01_runtime_path_persists_strong_signal() -> dict:
    result = run_market_analyzer_external_memory_path(
        request_id="rt-extmem-001",
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

    panel = result["panel"]
    passed = (
        result["status"] == "ok"
        and result["qualification_decision"] == "persist_candidate"
        and panel["persistence_decision"] == "committed"
        and panel["memory_id"] is not None
    )
    return {
        "case": "case_01_runtime_path_persists_strong_signal",
        "status": "passed" if passed else "failed",
        "details": {
            "qualification_decision": result["qualification_decision"],
            "persistence_decision": panel["persistence_decision"],
            "memory_id": panel["memory_id"],
        },
    }


def case_02_runtime_path_rejects_unconfirmed_low_quality_signal() -> dict:
    result = run_market_analyzer_external_memory_path(
        request_id="rt-extmem-002",
        symbol="XYZ",
        headline="Unconfirmed social rumor spikes speculative chatter",
        price_change_pct=0.8,
        sector="consumer",
        confirmation="unconfirmed",
        event_theme="speculative_move",
        macro_bias="mixed",
        route_mode="pm_route",
        source_type="social_scrape",
    )

    panel = result["panel"]
    passed = (
        result["status"] == "ok"
        and result["qualification_decision"] == "reject"
        and panel["persistence_decision"] == "rejected"
        and panel["rejection_reason"] is not None
    )
    return {
        "case": "case_02_runtime_path_rejects_unconfirmed_low_quality_signal",
        "status": "passed" if passed else "failed",
        "details": {
            "qualification_decision": result["qualification_decision"],
            "persistence_decision": panel["persistence_decision"],
            "rejection_reason": panel["rejection_reason"],
        },
    }


def run_probe() -> dict:
    cases = [
        case_01_runtime_path_persists_strong_signal(),
        case_02_runtime_path_rejects_unconfirmed_low_quality_signal(),
    ]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())
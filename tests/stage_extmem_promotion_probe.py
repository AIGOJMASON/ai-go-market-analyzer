from __future__ import annotations

from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
    run_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.promotion_path import (
    run_market_analyzer_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
    run_market_analyzer_external_memory_path,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
    run_market_analyzer_external_memory_retrieval,
)


def _seed_promotable_records() -> None:
    run_market_analyzer_external_memory_path(
        request_id="seed-prom-001",
        symbol="XLE",
        headline="Confirmed energy disruption event",
        price_change_pct=2.6,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_rebound",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="official_filing",
    )
    run_market_analyzer_external_memory_path(
        request_id="seed-prom-002",
        symbol="XLE",
        headline="Confirmed energy production update",
        price_change_pct=2.1,
        sector="energy",
        confirmation="confirmed",
        event_theme="energy_update",
        macro_bias="neutral",
        route_mode="pm_route",
        source_type="official_filing",
    )


def case_01_promotion_promotes_strong_retrieved_records() -> dict:
    _seed_promotable_records()
    result = run_market_analyzer_external_memory_promotion(
        limit=10,
        requester_profile="market_analyzer_reader",
        symbol="XLE",
        min_adjusted_weight=70,
    )

    artifact = result["artifact"]
    receipt = result["receipt"]

    passed = (
        result["status"] == "ok"
        and artifact is not None
        and artifact["artifact_type"] == "external_memory_promotion_artifact"
        and receipt["artifact_type"] == "external_memory_promotion_receipt"
        and artifact["decision"] in {"promoted", "hold"}
        and artifact["record_count"] >= 1
    )
    return {
        "case": "case_01_promotion_promotes_strong_retrieved_records",
        "status": "passed" if passed else "failed",
        "details": {
            "decision": artifact["decision"] if artifact else None,
            "promotion_score": artifact["promotion_score"] if artifact else None,
            "record_count": artifact["record_count"] if artifact else None,
        },
    }


def case_02_promotion_rejects_empty_retrieval_set() -> dict:
    retrieval_result = run_market_analyzer_external_memory_retrieval(
        limit=5,
        requester_profile="market_analyzer_reader",
        symbol="NO_MATCHING_SYMBOL_123",
    )
    result = run_external_memory_promotion(
        artifact=retrieval_result["artifact"] or {},
        receipt=retrieval_result["receipt"],
    )
    receipt = result["receipt"]

    passed = (
        result["status"] == "failed"
        and receipt["artifact_type"] == "external_memory_promotion_rejection_receipt"
        and receipt["failure_reason"] == "empty_record_set"
    )
    return {
        "case": "case_02_promotion_rejects_empty_retrieval_set",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": receipt["failure_reason"],
        },
    }


def case_03_promotion_rejects_misaligned_inputs() -> dict:
    artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "request_summary": {
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
        },
        "matched_count": 1,
        "returned_count": 1,
        "records": [
            {
                "memory_id": "mem_001",
                "qualification_record_id": "qual_001",
                "source_type": "official_filing",
                "trust_class": "verified",
                "source_quality_weight": 45.0,
                "adjusted_weight": 80.0,
                "contamination_penalty": 0.0,
                "payload_summary": {
                    "symbol": "XLE",
                    "sector": "energy",
                },
            }
        ],
    }
    receipt = {
        "artifact_type": "external_memory_retrieval_receipt",
        "requester_profile": "operator_reader",
        "target_child_core": "market_analyzer_v1",
        "limit": 5,
        "matched_count": 1,
        "returned_count": 1,
    }

    result = run_external_memory_promotion(artifact=artifact, receipt=receipt)
    rej = result["receipt"]

    passed = (
        result["status"] == "failed"
        and rej["artifact_type"] == "external_memory_promotion_rejection_receipt"
        and rej["failure_reason"] == "artifact_receipt_misalignment"
    )
    return {
        "case": "case_03_promotion_rejects_misaligned_inputs",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": rej["failure_reason"],
        },
    }


def case_04_promotion_rejects_blocked_trust_record() -> dict:
    artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "request_summary": {
            "requester_profile": "market_analyzer_reader",
            "target_child_core": "market_analyzer_v1",
            "limit": 5,
        },
        "matched_count": 1,
        "returned_count": 1,
        "records": [
            {
                "memory_id": "mem_002",
                "qualification_record_id": "qual_002",
                "source_type": "social_scrape",
                "trust_class": "unverifiable",
                "source_quality_weight": 10.0,
                "adjusted_weight": 55.0,
                "contamination_penalty": 10.0,
                "payload_summary": {
                    "symbol": "XYZ",
                    "sector": "consumer",
                },
            }
        ],
    }
    receipt = {
        "artifact_type": "external_memory_retrieval_receipt",
        "requester_profile": "market_analyzer_reader",
        "target_child_core": "market_analyzer_v1",
        "limit": 5,
        "matched_count": 1,
        "returned_count": 1,
    }

    result = run_external_memory_promotion(artifact=artifact, receipt=receipt)
    rej = result["receipt"]

    passed = (
        result["status"] == "failed"
        and rej["artifact_type"] == "external_memory_promotion_rejection_receipt"
        and rej["failure_reason"] == "blocked_trust_class_present"
    )
    return {
        "case": "case_04_promotion_rejects_blocked_trust_record",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result["status"],
            "failure_reason": rej["failure_reason"],
        },
    }


def run_probe() -> dict:
    cases = [
        case_01_promotion_promotes_strong_retrieved_records(),
        case_02_promotion_rejects_empty_retrieval_set(),
        case_03_promotion_rejects_misaligned_inputs(),
        case_04_promotion_rejects_blocked_trust_record(),
    ]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "results": cases}


if __name__ == "__main__":
    print(run_probe())
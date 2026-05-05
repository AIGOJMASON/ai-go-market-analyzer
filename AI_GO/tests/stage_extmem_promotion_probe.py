# tests/stage_extmem_promotion_probe.py
from __future__ import annotations

from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
    run_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.promotion_path import (
    run_market_analyzer_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
    run_market_analyzer_external_memory_retrieval,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
    run_market_analyzer_external_memory_admission,
)


def _mock_child_core_result(
    request_id: str,
    symbol: str = "XLE",
    sector: str = "energy",
    theme: str = "energy_rebound",
) -> dict:
    return {
        "status": "ok",
        "request_id": request_id,
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "runtime_panel": {
            "event_theme": theme,
            "macro_bias": "neutral",
        },
        "recommendation_panel": {
            "items": [{"symbol": symbol}],
        },
        "governance_panel": {
            "watcher_passed": True,
        },
        "closeout_status": "accepted",
        "sector": sector,
        "symbol": symbol,
        "closeout_id": f"closeout_{request_id}",
        "closeout_path": f"C:\\fake\\closeout\\{request_id}.json",
        "receipt_id": f"receipt_{request_id}",
        "receipt_path": f"C:\\fake\\receipt\\{request_id}.json",
        "watcher_status": "passed",
        "watcher_validation_id": f"watcher_{request_id}",
    }


def _seed_promotable_records() -> None:
    run_market_analyzer_external_memory_admission(
        _mock_child_core_result("seed-prom-001", "XLE", "energy", "energy_rebound")
    )
    run_market_analyzer_external_memory_admission(
        _mock_child_core_result("seed-prom-002", "XLE", "energy", "energy_rebound")
    )


def case_01_promotion_promotes_strong_retrieved_records() -> dict:
    _seed_promotable_records()
    result = run_market_analyzer_external_memory_promotion(
        limit=10,
        requester_profile="market_analyzer_reader",
        symbol="XLE",
        min_adjusted_weight=70,
    )

    artifact = result.get("artifact")
    receipt = result.get("receipt", {})

    passed = (
        result.get("status") == "ok"
        and isinstance(artifact, dict)
        and artifact.get("artifact_type") == "external_memory_promotion_artifact"
        and receipt.get("artifact_type") == "external_memory_promotion_receipt"
        and artifact.get("decision") in {"promoted", "hold"}
        and artifact.get("record_count", 0) >= 1
    )
    return {
        "case": "case_01_promotion_promotes_strong_retrieved_records",
        "status": "passed" if passed else "failed",
        "details": {
            "decision": artifact.get("decision") if isinstance(artifact, dict) else None,
            "promotion_score": artifact.get("promotion_score") if isinstance(artifact, dict) else None,
            "record_count": artifact.get("record_count") if isinstance(artifact, dict) else None,
        },
    }


def case_02_promotion_rejects_empty_retrieval_set() -> dict:
    retrieval_result = run_market_analyzer_external_memory_retrieval(
        limit=5,
        requester_profile="market_analyzer_reader",
        symbol="NO_MATCHING_SYMBOL_123",
    )
    result = run_external_memory_promotion(
        artifact=retrieval_result.get("artifact") or {},
        receipt=retrieval_result.get("receipt") or {},
    )
    receipt = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and receipt.get("artifact_type") == "external_memory_promotion_rejection_receipt"
        and receipt.get("failure_reason") == "empty_record_set"
    )
    return {
        "case": "case_02_promotion_rejects_empty_retrieval_set",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": receipt.get("failure_reason"),
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
    rej = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and rej.get("artifact_type") == "external_memory_promotion_rejection_receipt"
        and rej.get("failure_reason") == "artifact_receipt_misalignment"
    )
    return {
        "case": "case_03_promotion_rejects_misaligned_inputs",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": rej.get("failure_reason"),
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
    rej = result.get("receipt", {})

    passed = (
        result.get("status") == "failed"
        and rej.get("artifact_type") == "external_memory_promotion_rejection_receipt"
        and rej.get("failure_reason") == "blocked_trust_class_present"
    )
    return {
        "case": "case_04_promotion_rejects_blocked_trust_record",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": rej.get("failure_reason"),
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
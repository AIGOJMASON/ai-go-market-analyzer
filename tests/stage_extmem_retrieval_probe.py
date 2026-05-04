from __future__ import annotations

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


def _seed_records() -> None:
    run_market_analyzer_external_memory_admission(
        _mock_child_core_result("seed-extmem-001", "XLE", "energy", "energy_rebound")
    )
    run_market_analyzer_external_memory_admission(
        _mock_child_core_result("seed-extmem-002", "XOM", "energy", "energy_update")
    )
    run_market_analyzer_external_memory_admission(
        _mock_child_core_result("seed-extmem-003", "TSLA", "consumer", "speculative_move")
    )


def case_01_retrieval_returns_bounded_market_records() -> dict:
    _seed_records()
    result = run_market_analyzer_external_memory_retrieval(
        limit=10,
        requester_profile="market_analyzer_reader",
    )

    artifact = result.get("artifact")
    receipt = result.get("receipt", {})

    passed = (
        isinstance(artifact, dict)
        and artifact.get("artifact_type") == "external_memory_retrieval_artifact"
        and receipt.get("artifact_type") == "external_memory_retrieval_receipt"
        and artifact.get("returned_count", 0) >= 1
        and len(artifact.get("records", [])) <= 10
    )
    return {
        "case": "case_01_retrieval_returns_bounded_market_records",
        "status": "passed" if passed else "failed",
        "details": {
            "returned_count": artifact.get("returned_count") if isinstance(artifact, dict) else None,
            "matched_count": artifact.get("matched_count") if isinstance(artifact, dict) else None,
            "receipt_type": receipt.get("artifact_type"),
        },
    }


def case_02_retrieval_filters_by_symbol() -> dict:
    _seed_records()
    result = run_market_analyzer_external_memory_retrieval(
        limit=10,
        requester_profile="market_analyzer_reader",
        symbol="XLE",
    )

    artifact = result.get("artifact")
    records = artifact.get("records", []) if isinstance(artifact, dict) else []
    all_xle = all(
        isinstance(record, dict)
        and isinstance(record.get("payload_summary"), dict)
        and record["payload_summary"].get("symbol") == "XLE"
        for record in records
    )

    passed = (
        isinstance(artifact, dict)
        and artifact.get("artifact_type") == "external_memory_retrieval_artifact"
        and artifact.get("returned_count", 0) >= 1
        and all_xle
    )
    return {
        "case": "case_02_retrieval_filters_by_symbol",
        "status": "passed" if passed else "failed",
        "details": {
            "returned_count": artifact.get("returned_count") if isinstance(artifact, dict) else None,
            "all_xle": all_xle,
        },
    }


def case_03_retrieval_rejects_excessive_limit() -> dict:
    result = run_market_analyzer_external_memory_retrieval(
        limit=100,
        requester_profile="market_analyzer_reader",
    )

    receipt = result.get("receipt", {})
    passed = (
        receipt.get("artifact_type") == "external_memory_retrieval_failure_receipt"
        and receipt.get("failure_reason") == "limit_exceeds_profile_max"
    )
    return {
        "case": "case_03_retrieval_rejects_excessive_limit",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "receipt_type": receipt.get("artifact_type"),
            "failure_reason": receipt.get("failure_reason"),
        },
    }


def case_04_retrieval_rejects_invalid_profile() -> dict:
    result = run_market_analyzer_external_memory_retrieval(
        limit=5,
        requester_profile="unknown_reader",
    )

    receipt = result.get("receipt", {})
    passed = (
        receipt.get("artifact_type") == "external_memory_retrieval_failure_receipt"
        and receipt.get("failure_reason") == "invalid_requester_profile"
    )
    return {
        "case": "case_04_retrieval_rejects_invalid_profile",
        "status": "passed" if passed else "failed",
        "details": {
            "status_value": result.get("status"),
            "failure_reason": receipt.get("failure_reason"),
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
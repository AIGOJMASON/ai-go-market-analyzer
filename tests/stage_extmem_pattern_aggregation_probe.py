from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
    build_market_analyzer_pattern_context,
)


def _valid_promotion_artifact():
    return {
        "artifact_type": "external_memory_promotion",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "promotion_status": "promoted",
        "promoted_record_count": 3,
        "provenance_refs": [
            {"memory_id": "mem_001", "source_ref": "news:a"},
            {"memory_id": "mem_002", "source_ref": "news:b"},
            {"memory_id": "mem_003", "source_ref": "news:c"},
        ],
        "promoted_records": [
            {
                "memory_id": "mem_001",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "source_quality": "high",
                "trust_class": "trusted",
                "adjusted_weight": 82.0,
                "observed_at": "2026-03-20T16:00:00Z",
                "source_ref": "news:a",
            },
            {
                "memory_id": "mem_002",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "source_quality": "high",
                "trust_class": "trusted",
                "adjusted_weight": 79.0,
                "observed_at": "2026-03-22T16:00:00Z",
                "source_ref": "news:b",
            },
            {
                "memory_id": "mem_003",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "source_quality": "medium",
                "trust_class": "trusted",
                "adjusted_weight": 74.0,
                "observed_at": "2026-03-24T16:00:00Z",
                "source_ref": "news:c",
            },
        ],
    }


def _valid_promotion_receipt():
    return {
        "receipt_type": "external_memory_promotion_receipt",
        "artifact_type": "external_memory_promotion",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "status": "success",
    }


def case_01_pattern_aggregation_builds_expected_artifact():
    result = build_market_analyzer_pattern_context(
        _valid_promotion_artifact(),
        _valid_promotion_receipt(),
    )
    assert result["status"] == "ok"
    artifact = result["artifact"]
    receipt = result["receipt"]
    assert artifact["artifact_type"] == "external_memory_pattern_aggregation"
    assert artifact["recurrence_count"] == 3
    assert artifact["dominant_symbol"] == "XLE"
    assert artifact["dominant_sector"] == "energy"
    assert artifact["pattern_strength"] in {
        "forming_pattern",
        "strong_pattern",
        "dominant_pattern",
    }
    assert artifact["historical_confirmation"] == "moderate_confirmation"
    assert receipt["receipt_type"] == "external_memory_pattern_aggregation_receipt"


def case_02_pattern_aggregation_rejects_misaligned_receipt():
    bad_receipt = _valid_promotion_receipt()
    bad_receipt["target_core"] = "wrong_core"
    result = build_market_analyzer_pattern_context(
        _valid_promotion_artifact(),
        bad_receipt,
    )
    assert result["status"] == "failed"
    assert result["receipt"]["failure_reason"] == "artifact_receipt_misalignment"


def case_03_pattern_aggregation_rejects_empty_promoted_records():
    artifact = _valid_promotion_artifact()
    artifact["promoted_records"] = []
    artifact["promoted_record_count"] = 0
    result = build_market_analyzer_pattern_context(
        artifact,
        _valid_promotion_receipt(),
    )
    assert result["status"] == "failed"
    assert result["receipt"]["failure_reason"] == "empty_promoted_records"


def case_04_pattern_aggregation_rejects_non_promoted_status():
    artifact = _valid_promotion_artifact()
    artifact["promotion_status"] = "hold"
    result = build_market_analyzer_pattern_context(
        artifact,
        _valid_promotion_receipt(),
    )
    assert result["status"] == "failed"
    assert result["receipt"]["failure_reason"] == "promotion_status_not_promoted"


def run():
    tests = [
        case_01_pattern_aggregation_builds_expected_artifact,
        case_02_pattern_aggregation_rejects_misaligned_receipt,
        case_03_pattern_aggregation_rejects_empty_promoted_records,
        case_04_pattern_aggregation_rejects_non_promoted_status,
    ]
    passed = 0
    failed = 0
    results = []
    for test in tests:
        try:
            test()
            passed += 1
            results.append({"case": test.__name__, "status": "passed"})
        except AssertionError as exc:
            failed += 1
            results.append(
                {
                    "case": test.__name__,
                    "status": "failed",
                    "details": str(exc),
                }
            )
    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(run())
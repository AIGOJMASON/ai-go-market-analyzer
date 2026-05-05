from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.external_memory.return_path import (
    build_market_analyzer_return_packet,
)


def _promotion_artifact():
    return {
        "artifact_type": "external_memory_promotion",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "promotion_status": "promoted",
        "promoted_record_count": 2,
        "provenance_refs": [{"memory_id": "mem_001"}],
        "promoted_records": [
            {
                "memory_id": "mem_001",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "source_quality": "high",
                "trust_class": "trusted",
                "adjusted_weight": 80.0,
                "observed_at": "2026-03-20T16:00:00Z",
            },
            {
                "memory_id": "mem_002",
                "symbol": "XLE",
                "sector": "energy",
                "event_theme": "energy_rebound",
                "source_quality": "high",
                "trust_class": "trusted",
                "adjusted_weight": 76.0,
                "observed_at": "2026-03-22T16:00:00Z",
            },
        ],
    }


def _promotion_receipt():
    return {
        "receipt_type": "external_memory_promotion_receipt",
        "artifact_type": "external_memory_promotion",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "status": "success",
    }


def _pattern_artifact():
    return {
        "artifact_type": "external_memory_pattern_aggregation",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "aggregation_status": "aggregated",
        "recurrence_count": 4,
        "temporal_span_days": 6,
        "recency_weight": 0.85,
        "dominant_symbol": "XLE",
        "dominant_sector": "energy",
        "pattern_strength": "strong_pattern",
        "pattern_posture": "strong_pattern_context",
        "historical_confirmation": "high_confirmation",
        "pattern_summary": "4 promoted records around XLE across 6 day span; strong_pattern; high_confirmation.",
        "promoted_memory_ids": ["mem_001", "mem_002", "mem_003", "mem_004"],
        "promoted_record_count": 4,
        "provenance_refs": [{"memory_id": "mem_001"}],
    }


def _pattern_receipt():
    return {
        "receipt_type": "external_memory_pattern_aggregation_receipt",
        "artifact_type": "external_memory_pattern_aggregation",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "status": "success",
    }


def case_01_return_path_accepts_promotion_source():
    result = build_market_analyzer_return_packet(
        _promotion_artifact(),
        _promotion_receipt(),
    )
    assert result["status"] == "ok"
    assert result["artifact"]["artifact_type"] == "external_memory_return_packet"
    assert result["artifact"]["advisory_posture"] == "useful_context"


def case_02_return_path_accepts_pattern_source():
    result = build_market_analyzer_return_packet(
        _pattern_artifact(),
        _pattern_receipt(),
    )
    assert result["status"] == "ok"
    panel = result["artifact"]["external_memory_return_panel"]
    assert result["artifact"]["advisory_posture"] == "strong_context"
    assert panel["source_type"] == "pattern_aggregation"
    assert panel["pattern_strength"] == "strong_pattern"
    assert panel["historical_confirmation"] == "high_confirmation"


def case_03_return_path_rejects_invalid_receipt_type_for_pattern():
    bad_receipt = _promotion_receipt()
    result = build_market_analyzer_return_packet(
        _pattern_artifact(),
        bad_receipt,
    )
    assert result["status"] == "failed"
    assert result["receipt"]["failure_reason"] == "invalid_return_source_receipt_type"


def case_04_return_path_rejects_misaligned_source_inputs():
    bad_receipt = _pattern_receipt()
    bad_receipt["target_core"] = "wrong_core"
    result = build_market_analyzer_return_packet(
        _pattern_artifact(),
        bad_receipt,
    )
    assert result["status"] == "failed"
    assert result["receipt"]["failure_reason"] == "artifact_receipt_misalignment"


def run():
    tests = [
        case_01_return_path_accepts_promotion_source,
        case_02_return_path_accepts_pattern_source,
        case_03_return_path_rejects_invalid_receipt_type_for_pattern,
        case_04_return_path_rejects_misaligned_source_inputs,
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
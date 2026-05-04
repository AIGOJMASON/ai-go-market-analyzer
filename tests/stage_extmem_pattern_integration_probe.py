from __future__ import annotations

from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_runtime_integration import (
    apply_external_memory_pattern_flow,
)


def _promotion_artifact():
    return {
        "artifact_type": "external_memory_promotion",
        "target_core": "market_analyzer_v1",
        "requester_profile": "operator",
        "promotion_status": "promoted",
        "promoted_record_count": 3,
        "provenance_refs": [{"memory_id": "mem_001"}],
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


def case_01_pattern_panel_attaches():
    result = {
        "external_memory_promotion_artifact": _promotion_artifact(),
        "external_memory_promotion_receipt": _promotion_receipt(),
    }

    enriched = apply_external_memory_pattern_flow(result)

    assert "external_memory_pattern_panel" in enriched
    panel = enriched["external_memory_pattern_panel"]

    assert panel["source_type"] == "pattern_aggregation"
    assert panel["pattern_strength"] in {
        "forming_pattern",
        "strong_pattern",
        "dominant_pattern",
    }


def case_02_no_promotion_no_panel():
    result = {}

    enriched = apply_external_memory_pattern_flow(result)

    assert "external_memory_pattern_panel" not in enriched


def case_03_invalid_promotion_fails_safely():
    result = {
        "external_memory_promotion_artifact": {"invalid": True},
        "external_memory_promotion_receipt": {},
    }

    enriched = apply_external_memory_pattern_flow(result)

    assert "external_memory_pattern_panel" not in enriched


def run():
    tests = [
        case_01_pattern_panel_attaches,
        case_02_no_promotion_no_panel,
        case_03_invalid_promotion_fails_safely,
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
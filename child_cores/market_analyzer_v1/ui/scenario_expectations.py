from __future__ import annotations


SCENARIO_EXPECTATIONS = {
    "SCN-01": {
        "should_succeed": True,
        "expected_recommendation_count": 1,
        "expected_regime": "normal",
        "expected_trade_posture": "allowed",
        "notes": "Happy-path necessity rebound should produce one recommendation.",
    },
    "SCN-02": {
        "should_succeed": False,
        "expected_error_contains": "no necessity-qualified candidates available",
        "notes": "Non-necessity sector should be filtered out completely.",
    },
    "SCN-03": {
        "should_succeed": False,
        "expected_error_contains": "no rebound-validated candidates available",
        "notes": "Missing confirmation should block recommendation generation.",
    },
    "SCN-04": {
        "should_succeed": True,
        "expected_recommendation_count": 1,
        "expected_regime": "crisis",
        "expected_trade_posture": "conditional",
        "notes": "Current implementation permits structured output in crisis posture.",
    },
    "SCN-05": {
        "should_succeed": True,
        "expected_recommendation_count": 1,
        "expected_regime": "normal",
        "expected_trade_posture": "allowed",
        "notes": "Mixed set should narrow down to one valid candidate.",
    },
    "SCN-06": {
        "should_succeed": False,
        "expected_error_contains": "shock event is required for recommendation flow",
        "notes": "Unconfirmed shock must hard-fail.",
    },
}
from __future__ import annotations


def build_historical_replay_expectations() -> dict[str, dict]:
    return {
        "HIST-REPLAY-001": {
            "name": "necessity_energy_rebound",
            "should_succeed": True,
            "minimum_recommendation_count": 1,
            "expected_symbols_any_of": ["XLE"],
            "watcher_should_pass": True,
            "execution_allowed_must_be": False,
        },
        "HIST-REPLAY-002": {
            "name": "non_necessity_rejected",
            "should_succeed": False,
            "maximum_recommendation_count": 0,
            "expected_runtime_error_contains": "no necessity-qualified candidates available",
        },
        "HIST-REPLAY-003": {
            "name": "missing_confirmation_rejected",
            "should_succeed": False,
            "maximum_recommendation_count": 0,
            "expected_runtime_error_contains": "no rebound-validated candidates available",
        },
        "HIST-REPLAY-004": {
            "name": "crisis_regime_structured_output",
            "should_succeed": True,
            "minimum_recommendation_count": 1,
            "expected_symbols_any_of": ["XLE"],
            "watcher_should_pass": True,
            "execution_allowed_must_be": False,
        },
        "HIST-REPLAY-005": {
            "name": "mixed_candidate_filtering",
            "should_succeed": True,
            "minimum_recommendation_count": 1,
            "expected_symbols_any_of": ["XLE", "CORN"],
            "forbidden_symbols": ["QQQ"],
            "watcher_should_pass": True,
            "execution_allowed_must_be": False,
        },
        "HIST-REPLAY-006": {
            "name": "unconfirmed_shock_rejected",
            "should_succeed": False,
            "maximum_recommendation_count": 0,
            "expected_runtime_error_contains": "no rebound-validated candidates available",
        },
    }
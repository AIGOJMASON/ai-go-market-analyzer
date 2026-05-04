from __future__ import annotations

OUTCOME_CANDIDATE_REGISTRY = {
    "artifact_type": "market_outcome_candidate",
    "artifact_version": "v1",
    "required_fields": [
        "symbol",
        "reference_price",
        "event_theme",
        "expected_behavior",
        "direction",
    ],
    "allowed_directions": [
        "up",
        "down",
        "neutral",
        "unknown",
    ],
    "theme_direction_map": {
        "energy_rebound": "up",
        "tech_momentum": "up",
        "dip_rebound": "up",
        "breakout": "up",
        "continuation": "up",
        "inflation_pressure": "down",
        "rate_shift": "down",
        "hard_fade": "down",
        "confirmation_failure": "down",
        "unknown_event": "unknown",
    },
    "default_evaluation_window": "short_term",
    "default_confidence": 0.5,
}
from __future__ import annotations

ALLOWED_OUTCOME_CLASSES = {
    "follow_through",
    "failure",
    "stall",
}

ALLOWED_DIRECTIONAL_BIAS = {
    "bullish",
    "bearish",
    "neutral",
}

ALLOWED_SOURCE_TYPES = {
    "seed",
    "manual_backfill",
    "derived_from_historical_market",
    "derived_from_outcome_feedback",
}

LABELED_OUTCOME_ARTIFACT_TYPE = "historical_labeled_outcome"
LABELED_OUTCOME_RECEIPT_TYPE = "historical_labeled_outcome_receipt"

INDEX_FILE_NAMES = {
    "by_symbol": "labeled_outcomes_by_symbol.json",
    "by_event_theme": "labeled_outcomes_by_event_theme.json",
    "latest": "latest_labeled_outcomes.json",
}
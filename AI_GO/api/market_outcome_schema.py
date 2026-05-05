from __future__ import annotations

ALLOWED_MARKET_OUTCOME_SOURCES = [
    "market_feed",
    "manual",
]


def build_market_outcome_request(
    *,
    closeout_id: str,
    actual_outcome: str,
    source: str,
    observed_at: str,
    notes: str = "",
) -> dict:
    normalized_closeout_id = str(closeout_id or "").strip()
    normalized_actual_outcome = str(actual_outcome or "").strip()
    normalized_source = str(source or "").strip().lower()
    normalized_observed_at = str(observed_at or "").strip()
    normalized_notes = str(notes or "").strip()

    if not normalized_closeout_id:
        raise ValueError("missing_closeout_id")

    if not normalized_actual_outcome:
        raise ValueError("missing_actual_outcome")

    if not normalized_source:
        raise ValueError("missing_source")

    if normalized_source not in ALLOWED_MARKET_OUTCOME_SOURCES:
        raise ValueError("invalid_market_outcome_source")

    if not normalized_observed_at:
        raise ValueError("missing_observed_at")

    return {
        "closeout_id": normalized_closeout_id,
        "actual_outcome": normalized_actual_outcome,
        "source": normalized_source,
        "observed_at": normalized_observed_at,
        "notes": normalized_notes,
        "annotation_only": True,
    }
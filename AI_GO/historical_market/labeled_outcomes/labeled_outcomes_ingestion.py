from __future__ import annotations

from typing import Any, Dict

from AI_GO.historical_market.labeled_outcomes.labeled_outcomes_store import (
    persist_labeled_outcome,
)


def ingest_from_outcome_feedback_record(
    *,
    outcome_feedback_record: Dict[str, Any],
    source_type: str = "derived_from_outcome_feedback",
) -> Dict[str, Any]:
    """
    Converts an outcome feedback artifact into a historical labeled outcome record.
    """

    symbol = outcome_feedback_record.get("symbol")
    event_theme = outcome_feedback_record.get("event_theme")
    outcome_class = outcome_feedback_record.get("outcome_class")
    observed_at = (
        outcome_feedback_record.get("generated_at")
        or outcome_feedback_record.get("observed_at")
    )
    delta_pct = outcome_feedback_record.get("delta_pct")

    if outcome_class == "failed":
        mapped_outcome = "failure"
        directional_bias = "bullish"
    elif outcome_class == "worked":
        mapped_outcome = "follow_through"
        directional_bias = "bullish"
    else:
        mapped_outcome = "stall"
        directional_bias = "neutral"

    return persist_labeled_outcome(
        symbol=symbol,
        event_theme=event_theme,
        outcome_class=mapped_outcome,
        directional_bias=directional_bias,
        observed_at=observed_at,
        source_type=source_type,
        return_pct=float(delta_pct) if delta_pct is not None else None,
        headline=outcome_feedback_record.get("headline"),
        sector=outcome_feedback_record.get("sector"),
        source_request_id=outcome_feedback_record.get("request_id"),
        source_closeout_id=outcome_feedback_record.get("closeout_id"),
        notes="ingested from outcome feedback",
        metadata={
            "source_artifact_type": outcome_feedback_record.get("artifact_type"),
        },
    )


def ingest_manual_labeled_outcome(
    *,
    symbol: str,
    event_theme: str,
    outcome_class: str,
    directional_bias: str,
    observed_at: str,
    return_pct: float | None = None,
    hold_duration_bars: int | None = None,
    setup_type: str | None = None,
    headline: str | None = None,
    sector: str | None = None,
    notes: str | None = None,
) -> Dict[str, Any]:
    return persist_labeled_outcome(
        symbol=symbol,
        event_theme=event_theme,
        outcome_class=outcome_class,
        directional_bias=directional_bias,
        observed_at=observed_at,
        source_type="manual_backfill",
        return_pct=return_pct,
        hold_duration_bars=hold_duration_bars,
        setup_type=setup_type,
        headline=headline,
        sector=sector,
        notes=notes,
    )
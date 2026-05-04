from __future__ import annotations

from AI_GO.historical_market.labeled_outcomes.labeled_outcomes_store import (
    persist_labeled_outcome,
)


SEED_ROWS = [
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "follow_through",
        "directional_bias": "bullish",
        "observed_at": "2026-03-01T00:00:00Z",
        "return_pct": 2.8,
        "hold_duration_bars": 3,
        "headline": "Energy disruption confirmed",
        "sector": "energy",
    },
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "failure",
        "directional_bias": "bullish",
        "observed_at": "2026-03-04T00:00:00Z",
        "return_pct": -1.9,
        "hold_duration_bars": 2,
        "headline": "Energy rebound faded after open",
        "sector": "energy",
    },
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "stall",
        "directional_bias": "bullish",
        "observed_at": "2026-03-08T00:00:00Z",
        "return_pct": 0.1,
        "hold_duration_bars": 2,
        "headline": "Energy held but did not extend",
        "sector": "energy",
    },
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "follow_through",
        "directional_bias": "bullish",
        "observed_at": "2026-03-12T00:00:00Z",
        "return_pct": 3.4,
        "hold_duration_bars": 4,
        "headline": "Energy momentum extended on confirmation",
        "sector": "energy",
    },
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "failure",
        "directional_bias": "bullish",
        "observed_at": "2026-03-16T00:00:00Z",
        "return_pct": -2.2,
        "hold_duration_bars": 3,
        "headline": "Energy signal failed after shock headline",
        "sector": "energy",
    },
    {
        "symbol": "XLE",
        "event_theme": "energy_rebound",
        "outcome_class": "follow_through",
        "directional_bias": "bullish",
        "observed_at": "2026-03-20T00:00:00Z",
        "return_pct": 1.9,
        "hold_duration_bars": 2,
        "headline": "Energy recovered with follow-through",
        "sector": "energy",
    },
    {
        "symbol": "XLP",
        "event_theme": "defensive_rotation",
        "outcome_class": "follow_through",
        "directional_bias": "bullish",
        "observed_at": "2026-03-03T00:00:00Z",
        "return_pct": 1.1,
        "hold_duration_bars": 3,
        "headline": "Defensive rotation supported staples",
        "sector": "staples",
    },
    {
        "symbol": "XLP",
        "event_theme": "defensive_rotation",
        "outcome_class": "stall",
        "directional_bias": "bullish",
        "observed_at": "2026-03-10T00:00:00Z",
        "return_pct": 0.0,
        "hold_duration_bars": 2,
        "headline": "Staples held but lacked follow-through",
        "sector": "staples",
    },
    {
        "symbol": "XLU",
        "event_theme": "safety_bid",
        "outcome_class": "follow_through",
        "directional_bias": "bullish",
        "observed_at": "2026-03-05T00:00:00Z",
        "return_pct": 1.6,
        "hold_duration_bars": 3,
        "headline": "Utilities gained on safety bid",
        "sector": "utilities",
    },
    {
        "symbol": "XLU",
        "event_theme": "safety_bid",
        "outcome_class": "failure",
        "directional_bias": "bullish",
        "observed_at": "2026-03-18T00:00:00Z",
        "return_pct": -0.8,
        "hold_duration_bars": 2,
        "headline": "Utilities reversed after weak confirmation",
        "sector": "utilities",
    },
]


def main() -> None:
    written = 0
    for row in SEED_ROWS:
        persist_labeled_outcome(
            symbol=row["symbol"],
            event_theme=row["event_theme"],
            outcome_class=row["outcome_class"],
            directional_bias=row["directional_bias"],
            observed_at=row["observed_at"],
            source_type="seed",
            return_pct=row.get("return_pct"),
            hold_duration_bars=row.get("hold_duration_bars"),
            headline=row.get("headline"),
            sector=row.get("sector"),
            notes="seeded labeled outcome",
        )
        written += 1

    print({"status": "ok", "written": written})


if __name__ == "__main__":
    main()
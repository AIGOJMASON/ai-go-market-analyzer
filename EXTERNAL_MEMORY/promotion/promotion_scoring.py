from __future__ import annotations

from statistics import mean
from typing import Any, Dict, List


def _same_nonempty(values: List[str]) -> bool:
    if not values:
        return False
    first = values[0]
    if not first:
        return False
    return all(value == first for value in values)


def score_retrieved_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {
            "average_adjusted_weight": 0.0,
            "average_source_quality_weight": 0.0,
            "average_contamination_penalty": 0.0,
            "coherence_bonus": 0.0,
            "promotion_score": 0.0,
            "coherence_flags": [],
        }

    adjusted_weights = [float(record["adjusted_weight"]) for record in records]
    source_quality_weights = [float(record["source_quality_weight"]) for record in records]
    contamination_penalties = [
        float(record.get("contamination_penalty", 0.0)) for record in records
    ]

    symbols = [str(record["payload_summary"].get("symbol", "")) for record in records]
    sectors = [str(record["payload_summary"].get("sector", "")) for record in records]
    source_types = [str(record.get("source_type", "")) for record in records]

    coherence_bonus = 0.0
    coherence_flags: List[str] = []

    if _same_nonempty(symbols):
        coherence_bonus += 10.0
        coherence_flags.append("same_symbol")

    if _same_nonempty(sectors):
        coherence_bonus += 6.0
        coherence_flags.append("same_sector")

    if _same_nonempty(source_types):
        coherence_bonus += 4.0
        coherence_flags.append("same_source_type")

    average_adjusted_weight = round(mean(adjusted_weights), 2)
    average_source_quality_weight = round(mean(source_quality_weights), 2)
    average_contamination_penalty = round(mean(contamination_penalties), 2)

    promotion_score = round(
        average_adjusted_weight
        + average_source_quality_weight
        + coherence_bonus
        - average_contamination_penalty,
        2,
    )

    return {
        "average_adjusted_weight": average_adjusted_weight,
        "average_source_quality_weight": average_source_quality_weight,
        "average_contamination_penalty": average_contamination_penalty,
        "coherence_bonus": coherence_bonus,
        "promotion_score": promotion_score,
        "coherence_flags": coherence_flags,
    }
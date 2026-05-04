# AI_GO/EXTERNAL_MEMORY/promotion/promotion_scoring.py

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _payload_value(record: Dict[str, Any], key: str) -> str:
    payload_summary = record.get("payload_summary")
    if isinstance(payload_summary, dict):
        value = payload_summary.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / float(len(values)), 4)


def _dominant_count(values: List[str]) -> int:
    filtered = [value for value in values if value]
    if not filtered:
        return 0
    counts = Counter(filtered)
    return counts.most_common(1)[0][1]


def _coherence_bonus(records: List[Dict[str, Any]]) -> tuple[float, List[str]]:
    flags: List[str] = []
    bonus = 0.0

    symbols = [_payload_value(record, "symbol") for record in records]
    sectors = [_payload_value(record, "sector") for record in records]

    dominant_symbol_count = _dominant_count(symbols)
    dominant_sector_count = _dominant_count(sectors)
    record_count = len(records)

    if record_count > 0 and dominant_symbol_count == record_count:
        bonus += 8.0
        flags.append("symbol_coherent_full")

    if record_count > 1 and dominant_symbol_count >= 2:
        bonus += 4.0
        flags.append("symbol_coherent_partial")

    if record_count > 0 and dominant_sector_count == record_count:
        bonus += 6.0
        flags.append("sector_coherent_full")

    if record_count > 1 and dominant_sector_count >= 2:
        bonus += 3.0
        flags.append("sector_coherent_partial")

    trust_classes = [str(record.get("trust_class", "")).strip().lower() for record in records]
    if trust_classes and all(value == "verified" for value in trust_classes):
        bonus += 6.0
        flags.append("trust_verified_full")
    elif trust_classes and any(value == "verified" for value in trust_classes):
        bonus += 2.0
        flags.append("trust_verified_partial")

    if record_count >= 3:
        bonus += 5.0
        flags.append("record_count_depth")

    return round(bonus, 4), flags


def score_retrieved_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(records, list) or not records:
        return {
            "promotion_score": 0.0,
            "average_adjusted_weight": 0.0,
            "average_source_quality_weight": 0.0,
            "average_contamination_penalty": 0.0,
            "coherence_bonus": 0.0,
            "coherence_flags": [],
        }

    adjusted_weights = [_safe_float(record.get("adjusted_weight")) for record in records]
    source_quality_weights = [_safe_float(record.get("source_quality_weight")) for record in records]
    contamination_penalties = [_safe_float(record.get("contamination_penalty")) for record in records]

    average_adjusted_weight = _mean(adjusted_weights)
    average_source_quality_weight = _mean(source_quality_weights)
    average_contamination_penalty = _mean(contamination_penalties)

    coherence_bonus, coherence_flags = _coherence_bonus(records)

    promotion_score = round(
        average_adjusted_weight
        + (average_source_quality_weight * 0.35)
        - (average_contamination_penalty * 0.50)
        + coherence_bonus,
        4,
    )

    return {
        "promotion_score": promotion_score,
        "average_adjusted_weight": average_adjusted_weight,
        "average_source_quality_weight": average_source_quality_weight,
        "average_contamination_penalty": average_contamination_penalty,
        "coherence_bonus": coherence_bonus,
        "coherence_flags": coherence_flags,
    }
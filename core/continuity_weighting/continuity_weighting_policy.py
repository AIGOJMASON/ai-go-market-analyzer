# AI_GO/core/continuity_weighting/continuity_weighting_policy.py

from __future__ import annotations

from typing import Any, Dict

from .continuity_weighting_registry import PATTERN_STATUS_RULES, DEFAULT_DOMINANT_RULE


def classify_pattern_strength(recurrence_count: int) -> Dict[str, Any]:
    if recurrence_count in PATTERN_STATUS_RULES:
        return PATTERN_STATUS_RULES[recurrence_count]
    if recurrence_count >= 5:
        return DEFAULT_DOMINANT_RULE
    return {
        "status": "unknown",
        "weight": 0.0,
    }


def validate_pattern_record(pattern: Dict[str, Any]) -> bool:
    required_keys = [
        "continuity_key",
        "recurrence_count",
        "last_seen_timestamp",
        "source_surface",
        "event_class",
        "weight",
        "pattern_status",
    ]
    return all(key in pattern for key in required_keys)
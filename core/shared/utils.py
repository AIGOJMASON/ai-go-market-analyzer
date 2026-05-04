"""
AI_GO/core/shared/utils.py

General reusable helper functions for AI_GO.
"""

from __future__ import annotations

from typing import Any, Iterable, List


def ensure_list(value: Any) -> List[Any]:
    """
    Normalize a value into a list.

    - None -> []
    - list -> list
    - everything else -> [value]
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def compact_strings(values: Iterable[Any]) -> List[str]:
    """
    Return stripped non-empty string values from an iterable.
    """
    cleaned: List[str] = []
    for value in values:
        normalized = str(value).strip()
        if normalized:
            cleaned.append(normalized)
    return cleaned
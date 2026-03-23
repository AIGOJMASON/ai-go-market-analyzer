"""
AI_GO/core/shared/schemas.py

Lightweight structural validation helpers for AI_GO.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


def require_keys(payload: Mapping[str, Any], required_keys: Iterable[str]) -> None:
    """
    Ensure a mapping contains all required keys.

    Raises:
        ValueError: if payload is not a mapping or required keys are missing
    """
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")

    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")


def require_non_empty_string(value: Any, field_name: str) -> str:
    """
    Ensure a value is a non-empty string and return the stripped version.
    """
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string")
    return normalized
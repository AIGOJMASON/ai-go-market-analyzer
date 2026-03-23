"""
AI_GO/core/shared/timestamps.py

UTC timestamp helpers for AI_GO.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Return the current UTC datetime.
    """
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """
    Return the current UTC timestamp in ISO 8601 format.
    """
    return utc_now().isoformat()


def utc_compact() -> str:
    """
    Return a compact UTC timestamp for identifiers and filenames.
    """
    return utc_now().strftime("%Y%m%dT%H%M%SZ")
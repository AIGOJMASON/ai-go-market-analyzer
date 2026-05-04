"""
AI_GO/core/shared/ids.py

Governed identifier helpers for AI_GO.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def build_prefixed_id(prefix: str) -> str:
    """
    Build a governed prefixed identifier.

    Example:
        WR-RESEARCH-PACKET-20260317T010203Z-1A2B3C
    """
    normalized_prefix = str(prefix).strip().upper()
    if not normalized_prefix:
        raise ValueError("prefix may not be empty")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid4().hex[:6].upper()
    return f"{normalized_prefix}-{timestamp}-{suffix}"
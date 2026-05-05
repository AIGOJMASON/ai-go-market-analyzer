"""
AI_GO/core/runtime/status.py

Runtime status surface for AI_GO.

Purpose:
- provide a bounded runtime status payload
- expose lightweight status information for CLI and router surfaces

This module reports status only.
"""

from __future__ import annotations

from typing import Any, Dict

from core.shared.timestamps import utc_now_iso


def get_runtime_status() -> Dict[str, Any]:
    """
    Return a lightweight runtime status payload.
    """
    return {
        "system": "AI_GO",
        "runtime_layer": "core.runtime",
        "status": "available",
        "reported_at": utc_now_iso(),
    }
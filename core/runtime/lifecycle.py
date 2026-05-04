"""
AI_GO/core/runtime/lifecycle.py

Runtime lifecycle initialization for AI_GO.

Purpose:
- receive validated boot state from loader.py
- initialize bounded runtime lifecycle state
- expose a simple runtime activation payload

This module does not read boot files directly and does not perform command routing.
"""

from __future__ import annotations

from typing import Any, Dict

from core.shared.timestamps import utc_now_iso
from .loader import load_boot_state


def initialize_runtime() -> Dict[str, Any]:
    """
    Initialize the AI_GO runtime from validated boot state.

    Returns:
        Dict[str, Any]: runtime lifecycle payload
    """
    boot_state = load_boot_state()

    return {
        "status": "runtime_initialized",
        "system_id": boot_state["system_id"],
        "boot_id": boot_state.get("boot_id"),
        "boot_version": boot_state.get("boot_version"),
        "boot_order": boot_state.get("boot_order", []),
        "session_required": boot_state.get("session_required", False),
        "initialized_at": utc_now_iso(),
        "active_authority": "CORE",
    }
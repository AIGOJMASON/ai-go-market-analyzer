"""
AI_GO/core/continuity/continuity_registry.py

Registry declaration for the AI_GO continuity layer.
This file makes continuity module membership explicit.
"""

from __future__ import annotations

CONTINUITY_REGISTRY = {
    "layer": "core.continuity",
    "status": "active",
    "modules": [
        "_SMI_IMPLEMENTATION_LAYER.md",
        "smi.py",
        "continuity_state.py",
        "change_ledger.py",
        "unresolved_queue.py",
        "continuity_registry.py",
    ],
    "responsibilities": [
        "continuity_state_management",
        "accepted_change_recording",
        "unresolved_item_tracking",
        "continuity_status_reporting",
    ],
    "disallowed": [
        "research_screening",
        "research_trust_classification",
        "pm_strategy",
        "engine_refinement",
        "child_core_execution",
        "canon_authorship",
    ],
}
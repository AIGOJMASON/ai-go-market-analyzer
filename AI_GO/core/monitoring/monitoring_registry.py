"""
AI_GO/core/monitoring/monitoring_registry.py

Registry declaration for the AI_GO monitoring layer.
This file makes monitoring module membership explicit.
"""

from __future__ import annotations

MONITORING_REGISTRY = {
    "layer": "core.monitoring",
    "status": "active",
    "modules": [
        "_MONITORING_LAYER.md",
        "watcher.py",
        "sentinel.py",
        "verification.py",
        "transitions.py",
        "monitoring_registry.py",
    ],
    "responsibilities": [
        "artifact_verification",
        "transition_recording",
        "drift_detection",
        "monitoring_status_reporting",
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
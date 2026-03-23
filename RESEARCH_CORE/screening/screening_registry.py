"""
RESEARCH_CORE.screening.screening_registry

Registry declaration for the screening layer.
This file declares the screening module surface and boundaries.
"""

from __future__ import annotations

SCREENING_REGISTRY = {
    "layer": "RESEARCH_CORE.screening",
    "status": "active",
    "modules": [
        "screening.py",
        "source_credibility.py",
        "signal_filter.py",
        "screening_registry.py",
    ],
    "responsibilities": [
        "signal_structure_checks",
        "source_readiness_checks",
        "screening_outcome_declaration",
    ],
    "downstream_targets": [
        "RESEARCH_CORE.trust",
        "RESEARCH_CORE.packets",
    ],
    "disallowed": [
        "trust_class_assignment",
        "packet_emission",
        "pm_strategy",
        "child_core_execution",
    ],
}
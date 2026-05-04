"""
RESEARCH_CORE.intake.intake_registry

Registry declaration for the intake layer.
This file makes the intake surface explicit and bounded.
"""

from __future__ import annotations

INTAKE_REGISTRY = {
    "layer": "RESEARCH_CORE.intake",
    "status": "active",
    "modules": [
        "intake.py",
        "source_intake.py",
        "intake_registry.py",
    ],
    "responsibilities": [
        "raw_signal_normalization",
        "source_reference_normalization",
        "intake_shape_validation",
    ],
    "downstream_targets": [
        "RESEARCH_CORE.screening.screening",
    ],
    "disallowed": [
        "trust_classification",
        "packet_emission",
        "pm_strategy",
        "child_core_execution",
    ],
}
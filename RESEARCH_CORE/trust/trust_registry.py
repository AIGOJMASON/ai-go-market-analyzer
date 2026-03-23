"""
RESEARCH_CORE.trust.trust_registry

Registry declaration for the trust layer.
This file declares the trust module surface and authority boundaries.
"""

from __future__ import annotations

TRUST_REGISTRY = {
    "layer": "RESEARCH_CORE.trust",
    "status": "active",
    "modules": [
        "trust.py",
        "trust_model.py",
        "trust_registry.py",
    ],
    "responsibilities": [
        "explicit_trust_classification",
        "trust_rationale_declaration",
        "screened_input_handling_state",
    ],
    "downstream_targets": [
        "RESEARCH_CORE.packets.packet_builder",
    ],
    "disallowed": [
        "screening_ownership",
        "packet_emission",
        "pm_strategy",
        "child_core_execution",
    ],
}
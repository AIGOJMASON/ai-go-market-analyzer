"""
RESEARCH_CORE.packets.packet_registry

Registry declaration for the packets layer.
This file declares the research packet emission surface and boundaries.
"""

from __future__ import annotations

PACKET_REGISTRY = {
    "layer": "RESEARCH_CORE.packets",
    "status": "active",
    "modules": [
        "packet_builder.py",
        "packet_schema.md",
        "packet_registry.py",
    ],
    "responsibilities": [
        "research_packet_construction",
        "packet_shape_alignment",
        "downstream_handoff_artifact_emission",
    ],
    "upstream_dependencies": [
        "RESEARCH_CORE.intake",
        "RESEARCH_CORE.screening",
        "RESEARCH_CORE.trust",
    ],
    "disallowed": [
        "trust_class_assignment",
        "pm_strategy",
        "child_core_execution",
        "canon_authorship",
    ],
}
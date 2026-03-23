"""
PM_CORE.inheritance.inheritance_registry

Registry declaration for the inheritance layer.
This file declares the inheritance module surface and boundaries.
"""

from __future__ import annotations

INHERITANCE_REGISTRY = {
    "layer": "PM_CORE.inheritance",
    "status": "active",
    "modules": [
        "inheritance.py",
        "inheritance_packet_builder.py",
        "inheritance_registry.py",
        "packet_schema.md",
    ],
    "responsibilities": [
        "inheritance_handoff_preparation",
        "inheritance_packet_construction",
        "child_core_targeted_propagation_artifacts",
    ],
    "upstream_dependencies": [
        "PM_CORE.refinement",
    ],
    "downstream_targets": [
        "child_cores",
        "PM_CORE.interfaces",
    ],
    "disallowed": [
        "direct_child_core_execution",
        "research_intake",
        "runtime_boot_control",
        "canon_authorship",
    ],
}
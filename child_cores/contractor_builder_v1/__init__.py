"""
contractor_builder_v1

Governed child-core family for construction and contractor operations inside AI_GO.

This package establishes the contractor family as a bounded, auditable, receipt-backed
domain surface composed of authority-bounded modules such as workflow, change,
decision logging, compliance, routing, reporting, and weekly orchestration.

Design posture:
- governed child-core family
- append-only records where specified
- PM-gated release where specified
- no autonomous scope or schedule mutation
- numbers first, then summary
"""

from .registry.contractor_registry import CONTRACTOR_BUILDER_REGISTRY
from .registry.module_registry import CONTRACTOR_MODULE_REGISTRY
from .registry.authority_map import CONTRACTOR_AUTHORITY_MAP

__all__ = [
    "CONTRACTOR_BUILDER_REGISTRY",
    "CONTRACTOR_MODULE_REGISTRY",
    "CONTRACTOR_AUTHORITY_MAP",
]
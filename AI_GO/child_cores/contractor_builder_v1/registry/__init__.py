"""
Registry surfaces for contractor_builder_v1.

This package exposes the family registry, module registry, and authority map that
define the lawful shape of the contractor child-core family.
"""

from .contractor_registry import CONTRACTOR_BUILDER_REGISTRY
from .module_registry import CONTRACTOR_MODULE_REGISTRY
from .authority_map import CONTRACTOR_AUTHORITY_MAP

__all__ = [
    "CONTRACTOR_BUILDER_REGISTRY",
    "CONTRACTOR_MODULE_REGISTRY",
    "CONTRACTOR_AUTHORITY_MAP",
]
"""
Assumption log surfaces for contractor_builder_v1.

This package owns the structured assumption governance branch for contractor projects:
- assumption schema
- append-only assumption runtime
- invalidation conversion helpers
- assumption receipts
"""

from .assumption_schema import (
    ASSUMPTION_SCHEMA_VERSION,
    ASSUMPTION_SOURCE_TYPE_ENUM,
    build_assumption_entry,
    validate_assumption_entry,
    get_assumption_entry_template,
)
from .assumption_runtime import (
    get_assumptions_path,
    create_assumption_record,
    append_assumption_record,
    transition_assumption_status,
)
from .invalidation_conversion import (
    INVALIDATION_CONVERSION_OPTIONS,
    build_invalidation_conversion_record,
    validate_invalidation_conversion_option,
)
from .assumption_receipt_builder import (
    build_assumption_receipt,
    write_assumption_receipt,
)

__all__ = [
    "ASSUMPTION_SCHEMA_VERSION",
    "ASSUMPTION_SOURCE_TYPE_ENUM",
    "build_assumption_entry",
    "validate_assumption_entry",
    "get_assumption_entry_template",
    "get_assumptions_path",
    "create_assumption_record",
    "append_assumption_record",
    "transition_assumption_status",
    "INVALIDATION_CONVERSION_OPTIONS",
    "build_invalidation_conversion_record",
    "validate_invalidation_conversion_option",
    "build_assumption_receipt",
    "write_assumption_receipt",
]
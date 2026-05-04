"""
Risk register surfaces for contractor_builder_v1.

This package owns the human-centered operational risk branch for contractor projects:
- risk schema
- risk runtime
- weekly review runtime
- risk receipts
"""

from .risk_schema import (
    RISK_SCHEMA_VERSION,
    RISK_CATEGORY_ENUM,
    build_risk_entry,
    validate_risk_entry,
    get_risk_entry_template,
)
from .risk_runtime import (
    get_risks_path,
    create_risk_record,
    append_risk_record,
    transition_risk_status,
)
from .review_runtime import (
    build_risk_review_record,
    review_risk_entry,
    risk_requires_review,
)
from .risk_receipt_builder import (
    build_risk_receipt,
    write_risk_receipt,
)

__all__ = [
    "RISK_SCHEMA_VERSION",
    "RISK_CATEGORY_ENUM",
    "build_risk_entry",
    "validate_risk_entry",
    "get_risk_entry_template",
    "get_risks_path",
    "create_risk_record",
    "append_risk_record",
    "transition_risk_status",
    "build_risk_review_record",
    "review_risk_entry",
    "risk_requires_review",
    "build_risk_receipt",
    "write_risk_receipt",
]
"""
Decision log surfaces for contractor_builder_v1.

This package owns the internal decision governance branch for contractor projects:
- decision schema
- dual acknowledgment policy
- decision runtime
- decision receipts
"""

from .decision_schema import (
    DECISION_SCHEMA_VERSION,
    build_decision_entry,
    validate_decision_entry,
    get_decision_entry_template,
)
from .dual_ack_policy import (
    can_submit_decision,
    can_enter_approver_review,
    can_approve_decision,
    can_reject_decision,
    apply_requester_signature,
    apply_approver_signature,
)
from .decision_runtime import (
    get_decisions_path,
    create_decision_record,
    append_decision_record,
    transition_decision_status,
)
from .decision_receipt_builder import (
    build_decision_receipt,
    write_decision_receipt,
)

__all__ = [
    "DECISION_SCHEMA_VERSION",
    "build_decision_entry",
    "validate_decision_entry",
    "get_decision_entry_template",
    "can_submit_decision",
    "can_enter_approver_review",
    "can_approve_decision",
    "can_reject_decision",
    "apply_requester_signature",
    "apply_approver_signature",
    "get_decisions_path",
    "create_decision_record",
    "append_decision_record",
    "transition_decision_status",
    "build_decision_receipt",
    "write_decision_receipt",
]
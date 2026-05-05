"""
Shared governance surfaces for contractor_builder_v1.

This package contains the contractor family's common identity rules, integrity rules,
receipt triggers, append-only helpers, shared enums, and shared reference contracts.
"""

from .identity import (
    build_change_packet_id,
    build_decision_id,
    build_phase_id,
    build_project_id,
    build_receipt_id,
    build_report_id,
    build_risk_id,
    build_snapshot_id,
)
from .integrity import (
    canonical_json_dumps,
    compute_hash_for_mapping,
    compute_hash_for_text,
    with_integrity_block,
)
from .receipt_policy import (
    CONTRACTOR_RECEIPT_POLICY,
    get_required_receipt_events,
    receipt_required_for_event,
)
from .append_only_policy import (
    APPEND_ONLY_MODULES,
    assert_append_only_module,
    build_supersedes_link,
    module_requires_append_only,
)
from .shared_enums import SHARED_ENUMS
from .reference_contracts import (
    CONTRACTOR_REFERENCE_CONTRACTS,
    get_required_reference_keys,
)

__all__ = [
    "build_change_packet_id",
    "build_decision_id",
    "build_phase_id",
    "build_project_id",
    "build_receipt_id",
    "build_report_id",
    "build_risk_id",
    "build_snapshot_id",
    "canonical_json_dumps",
    "compute_hash_for_mapping",
    "compute_hash_for_text",
    "with_integrity_block",
    "CONTRACTOR_RECEIPT_POLICY",
    "get_required_receipt_events",
    "receipt_required_for_event",
    "APPEND_ONLY_MODULES",
    "assert_append_only_module",
    "build_supersedes_link",
    "module_requires_append_only",
    "SHARED_ENUMS",
    "CONTRACTOR_REFERENCE_CONTRACTS",
    "get_required_reference_keys",
]
"""
Change surfaces for contractor_builder_v1.

This package owns the lawful controlled-mutation branch for contractor projects:
- change packet schema
- pricing logic
- dead-time costing
- schedule delta logic
- approval flow
- change runtime
- change receipts
- customer-impact signoff policy
- change closeout guard
- change signoff status runtime
"""

from .change_schema import (
    CHANGE_SCHEMA_VERSION,
    build_change_packet,
    validate_change_packet,
    get_change_packet_template,
)
from .pricing_model import (
    build_cost_delta_block,
    compute_total_change_order_amount,
)
from .dead_time_model import (
    build_dead_time_cost_block,
    compute_dead_time_cost_estimate,
)
from .schedule_delta_model import (
    build_time_delta_block,
    compute_total_schedule_delta_days,
)
from .approval_runtime import (
    can_submit_change_packet,
    can_move_to_pending_approvals,
    can_approve_change_packet,
    apply_requester_signature,
    apply_approver_signature,
    apply_pm_signature,
)
from .change_runtime import (
    get_change_packets_path,
    get_change_approvals_path,
    create_change_packet_record,
    append_change_packet_record,
    append_change_approval_event,
    transition_change_packet_status,
    read_change_packet_history,
    get_latest_change_packet,
    list_latest_change_packets,
)
from .change_receipt_builder import (
    build_change_receipt,
    write_change_receipt,
)
from .change_signoff_policy import (
    build_change_signoff_policy_summary,
    change_requires_customer_signoff,
    is_change_signoff_resolved,
    is_blocking_unresolved_change,
)
from .change_signoff_status_runtime import (
    get_change_signoff_status_path,
    build_initial_change_signoff,
    mark_sent as mark_change_signoff_sent,
    mark_signed as mark_change_signoff_signed,
    mark_declined as mark_change_signoff_declined,
    append_change_signoff_status,
    get_latest_change_signoff_status,
    list_change_signoff_status_history,
)
from .change_closeout_guard import (
    get_latest_change_packets_for_phase,
    get_blocking_unresolved_changes,
    phase_has_blocking_unresolved_changes,
    build_change_closeout_guard_summary,
)

__all__ = [
    "CHANGE_SCHEMA_VERSION",
    "build_change_packet",
    "validate_change_packet",
    "get_change_packet_template",
    "build_cost_delta_block",
    "compute_total_change_order_amount",
    "build_dead_time_cost_block",
    "compute_dead_time_cost_estimate",
    "build_time_delta_block",
    "compute_total_schedule_delta_days",
    "can_submit_change_packet",
    "can_move_to_pending_approvals",
    "can_approve_change_packet",
    "apply_requester_signature",
    "apply_approver_signature",
    "apply_pm_signature",
    "get_change_packets_path",
    "get_change_approvals_path",
    "create_change_packet_record",
    "append_change_packet_record",
    "append_change_approval_event",
    "transition_change_packet_status",
    "read_change_packet_history",
    "get_latest_change_packet",
    "list_latest_change_packets",
    "build_change_receipt",
    "write_change_receipt",
    "build_change_signoff_policy_summary",
    "change_requires_customer_signoff",
    "is_change_signoff_resolved",
    "is_blocking_unresolved_change",
    "get_change_signoff_status_path",
    "build_initial_change_signoff",
    "mark_change_signoff_sent",
    "mark_change_signoff_signed",
    "mark_change_signoff_declined",
    "append_change_signoff_status",
    "get_latest_change_signoff_status",
    "list_change_signoff_status_history",
    "get_latest_change_packets_for_phase",
    "get_blocking_unresolved_changes",
    "phase_has_blocking_unresolved_changes",
    "build_change_closeout_guard_summary",
]
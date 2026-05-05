"""
Receipt policy for contractor_builder_v1.

This module defines which event classes require receipts across the contractor family.
It does not write receipts. It declares when receipt emission is mandatory.
"""

from __future__ import annotations

from typing import Dict, List, Set


CONTRACTOR_RECEIPT_POLICY: Dict[str, Set[str]] = {
    "project_intake": {
        "create_project",
        "lock_baseline",
    },
    "workflow": {
        "create_phase_plan",
        "update_phase_state",
        "record_client_signoff",
        "record_phase_drift",
    },
    "change": {
        "create_change_packet",
        "price_change_packet",
        "submit_change_packet",
        "approve_change_packet",
        "reject_change_packet",
        "archive_change_packet",
        "send_change_signoff",
        "record_change_signoff",
        "resend_change_signoff",
    },
    "decision_log": {
        "create_decision",
        "submit_decision",
        "review_decision",
        "approve_decision",
        "reject_decision",
        "export_decision",
    },
    "risk_register": {
        "create_risk",
        "review_risk",
        "change_risk_status",
    },
    "assumption_log": {
        "create_assumption",
        "change_assumption_status",
        "invalidate_assumption",
    },
    "comply": {
        "lock_compliance_snapshot",
        "record_permit",
        "record_inspection",
        "run_code_lookup",
    },
    "router": {
        "store_schedule_blocks",
        "run_conflict_scan",
        "write_conflict_report",
    },
    "oracle": {
        "publish_snapshot",
        "classify_shock",
        "create_projection",
        "create_risk_flag",
        "create_procurement_advisory",
    },
    "report": {
        "generate_project_weekly",
        "generate_portfolio_weekly",
        "approve_report",
        "archive_report",
    },
    "weekly_cycle": {
        "run_weekly_cycle",
    },
    "projection": {
        "persist_latest_payload",
    },
}


def receipt_required_for_event(module_id: str, event_type: str) -> bool:
    """
    Return True if a receipt is required for the module/event pair.
    """
    return event_type in CONTRACTOR_RECEIPT_POLICY.get(module_id, set())


def get_required_receipt_events(module_id: str) -> List[str]:
    """
    Return the sorted list of receipt-required events for a module.
    """
    return sorted(CONTRACTOR_RECEIPT_POLICY.get(module_id, set()))
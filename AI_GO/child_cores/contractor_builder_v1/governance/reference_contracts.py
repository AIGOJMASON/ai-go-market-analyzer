"""
Reference contracts for contractor_builder_v1.

This module defines the canonical required keys for shared contractor references.
It is used to keep schemas and adapters aligned across modules.
"""

from __future__ import annotations

from typing import Dict, List


CONTRACTOR_REFERENCE_CONTRACTS: Dict[str, List[str]] = {
    "project_ref": [
        "project_id",
    ],
    "phase_ref": [
        "project_id",
        "phase_id",
    ],
    "decision_ref": [
        "project_id",
        "decision_id",
    ],
    "change_packet_ref": [
        "project_id",
        "phase_id",
        "change_packet_id",
    ],
    "change_signoff_ref": [
        "project_id",
        "phase_id",
        "change_packet_id",
        "status",
    ],
    "risk_ref": [
        "project_id",
        "risk_id",
    ],
    "assumption_ref": [
        "project_id",
        "assumption_id",
    ],
    "snapshot_ref": [
        "jurisdiction_id",
        "snapshot_id",
    ],
    "report_ref": [
        "project_id",
        "weekly_report_id",
    ],
    "portfolio_report_ref": [
        "portfolio_id",
        "portfolio_report_id",
    ],
    "inspection_ref": [
        "project_id",
        "phase_id",
        "inspection_event_id",
        "snapshot_id",
    ],
    "permit_ref": [
        "project_id",
        "permit_id",
        "snapshot_id",
    ],
    "receipt_ref": [
        "receipt_id",
    ],
    "integrity_ref": [
        "linked_receipts",
    ],
}


def get_required_reference_keys(contract_name: str) -> List[str]:
    """
    Return the required reference keys for a named contract.
    """
    if contract_name not in CONTRACTOR_REFERENCE_CONTRACTS:
        raise KeyError(f"Unknown contractor reference contract: {contract_name}")
    return list(CONTRACTOR_REFERENCE_CONTRACTS[contract_name])
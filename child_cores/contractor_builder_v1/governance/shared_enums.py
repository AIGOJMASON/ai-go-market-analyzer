"""
Shared enums for contractor_builder_v1.

This module centralizes reusable status labels, approval labels, impact labels,
and related family-wide enum sets to reduce schema drift.
"""

from __future__ import annotations

from typing import Dict, List


SHARED_ENUMS: Dict[str, List[str]] = {
    "approval_status": [
        "pending_pm_review",
        "approved_for_release",
        "returned_for_revision",
        "archived_no_release",
    ],
    "signature_state": [
        "missing",
        "present",
    ],
    "impact_level": [
        "Low",
        "Moderate",
        "High",
    ],
    "probability_level": [
        "Low",
        "Moderate",
        "High",
    ],
    "severity_level": [
        "Low",
        "Moderate",
        "High",
    ],
    "validation_status": [
        "Unverified",
        "Verified",
        "Invalidated",
        "Archived",
    ],
    "risk_status": [
        "Open",
        "Monitoring",
        "Mitigated",
        "Occurred",
        "Closed",
    ],
    "change_packet_status": [
        "draft",
        "requester_submitted",
        "pm_review",
        "priced",
        "pending_approvals",
        "approved",
        "rejected",
        "archived",
    ],
    "decision_status": [
        "draft",
        "requester_submitted",
        "approver_review",
        "approved",
        "rejected",
        "archived",
    ],
    "phase_status": [
        "not_started",
        "in_progress",
        "blocked",
        "awaiting_signoff",
        "complete",
        "closed",
    ],
    "inspection_result": [
        "passed",
        "failed",
        "conditional",
    ],
    "permit_status": [
        "applied",
        "issued",
        "closed",
        "expired",
    ],
    "owner_acknowledged": [
        "Yes",
        "No",
        "Not_Required",
    ],
}
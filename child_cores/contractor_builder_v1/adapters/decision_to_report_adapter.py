"""
Decision to report adapter for contractor_builder_v1.

This adapter compresses decision records into a bounded reporting snapshot.
It does not alter decision authority or expose hidden internal content.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_decision_report_snapshot(
    *,
    decision_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded decision snapshot for reporting.
    """
    approved_decisions = [
        record for record in decision_records
        if record.get("decision_status") == "approved"
    ]
    review_decisions = [
        record for record in decision_records
        if record.get("decision_status") == "approver_review"
    ]

    approved_reference_labels = [
        record.get("reporting_refs", {}).get("owner_report_reference_label", "")
        for record in approved_decisions
        if record.get("reporting_refs", {}).get("may_reference_in_owner_reports", False)
    ]

    return {
        "decision_count": len(decision_records),
        "approved_decision_count": len(approved_decisions),
        "review_decision_count": len(review_decisions),
        "approved_reference_labels": [
            label for label in approved_reference_labels if label
        ],
    }
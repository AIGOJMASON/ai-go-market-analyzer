"""
Decision projection for contractor_builder_v1.

This module builds a bounded decision summary panel from internal decision records.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_decision_projection(
    *,
    decision_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a bounded decisions panel.
    """
    approved_count = sum(
        1 for record in decision_records
        if record.get("decision_status") == "approved"
    )
    submitted_count = sum(
        1 for record in decision_records
        if record.get("decision_status") == "requester_submitted"
    )
    review_count = sum(
        1 for record in decision_records
        if record.get("decision_status") == "approver_review"
    )

    latest_items = [
        {
            "decision_id": record.get("decision_id", ""),
            "title": record.get("title", ""),
            "decision_type": record.get("decision_type", ""),
            "decision_status": record.get("decision_status", ""),
            "expected_cost_delta_amount": record.get("declared_impact", {}).get(
                "expected_cost_delta_amount"
            ),
            "expected_schedule_delta_days": record.get("declared_impact", {}).get(
                "expected_schedule_delta_days"
            ),
        }
        for record in decision_records[-5:]
    ]

    return {
        "decision_count": len(decision_records),
        "approved_count": approved_count,
        "submitted_count": submitted_count,
        "review_count": review_count,
        "latest_items": latest_items,
    }
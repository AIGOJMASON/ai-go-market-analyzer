"""
Comply to report adapter for contractor_builder_v1.

This adapter translates a compliance snapshot into the bounded structure expected
by report consumers. It does not interpret legal meaning or mutate compliance state.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_compliance_report_snapshot(
    *,
    compliance_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a bounded compliance report snapshot.
    """
    permits = list(compliance_snapshot.get("permits", []))
    inspections = list(compliance_snapshot.get("inspections", []))

    pending_permits = [
        permit.get("permit_type", "")
        for permit in permits
        if permit.get("status") != "approved"
    ]
    failed_or_open_inspections = [
        inspection.get("inspection_type", "")
        for inspection in inspections
        if not inspection.get("passed", False)
    ]

    return {
        "blocking": bool(compliance_snapshot.get("blocking", False)),
        "blocking_count": int(compliance_snapshot.get("blocking_count", 0)),
        "permit_count": len(permits),
        "inspection_count": len(inspections),
        "pending_permits": pending_permits,
        "failed_or_open_inspections": failed_or_open_inspections,
    }
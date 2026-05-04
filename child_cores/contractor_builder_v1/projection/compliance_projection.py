"""
Compliance projection for contractor_builder_v1.

This module builds a bounded compliance summary panel from the current compliance
snapshot.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_compliance_projection(
    *,
    compliance_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a bounded compliance panel.
    """
    permits = list(compliance_snapshot.get("permits", []))
    inspections = list(compliance_snapshot.get("inspections", []))

    blocking_permits = [
        permit for permit in permits
        if permit.get("blocking") and permit.get("status") != "approved"
    ]
    blocking_inspections = [
        inspection for inspection in inspections
        if inspection.get("blocking") and not inspection.get("passed")
    ]

    return {
        "blocking": bool(compliance_snapshot.get("blocking", False)),
        "blocking_count": int(compliance_snapshot.get("blocking_count", 0)),
        "permit_count": len(permits),
        "inspection_count": len(inspections),
        "blocking_permits": [
            {
                "permit_type": permit.get("permit_type", ""),
                "status": permit.get("status", ""),
            }
            for permit in blocking_permits
        ],
        "blocking_inspections": [
            {
                "inspection_type": inspection.get("inspection_type", ""),
                "status": inspection.get("status", ""),
                "passed": inspection.get("passed", False),
            }
            for inspection in blocking_inspections
        ],
    }
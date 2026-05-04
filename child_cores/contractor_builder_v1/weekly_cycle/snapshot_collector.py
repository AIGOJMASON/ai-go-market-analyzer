"""
Snapshot collector for contractor_builder_v1.

This module creates bounded project snapshot packets for weekly orchestration.
It is intentionally read-only and expects structured inputs from upstream module
surfaces rather than pulling hidden state magically.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_project_module_snapshot(
    *,
    project_id: str,
    workflow_snapshot: Dict[str, Any],
    change_records: List[Dict[str, Any]],
    compliance_snapshot: Dict[str, Any],
    router_snapshot: Dict[str, Any],
    oracle_snapshot: Dict[str, Any],
    decision_records: List[Dict[str, Any]],
    risk_records: List[Dict[str, Any]],
    assumption_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build one bounded project snapshot packet for weekly orchestration.
    """
    return {
        "project_id": project_id,
        "workflow_snapshot": dict(workflow_snapshot),
        "change_records": list(change_records),
        "compliance_snapshot": dict(compliance_snapshot),
        "router_snapshot": dict(router_snapshot),
        "oracle_snapshot": dict(oracle_snapshot),
        "decision_records": list(decision_records),
        "risk_records": list(risk_records),
        "assumption_records": list(assumption_records),
    }


def collect_project_snapshots(
    *,
    project_snapshots: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Return bounded project snapshots as-is after lightweight validation.
    """
    collected: List[Dict[str, Any]] = []

    for snapshot in project_snapshots:
        project_id = str(snapshot.get("project_id", "")).strip()
        if not project_id:
            raise ValueError("Each project snapshot requires a non-empty project_id")
        collected.append(dict(snapshot))

    return collected
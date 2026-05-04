"""
Project projection for contractor_builder_v1.

This module builds the read-only project-facing panel used by the operator payload.
"""

from __future__ import annotations

from typing import Any, Dict


def build_project_projection(
    *,
    project_profile: Dict[str, Any],
    baseline_lock: Dict[str, Any],
    workflow_snapshot: Dict[str, Any],
    latest_project_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the project-facing projection block.
    """
    deterministic_block = latest_project_report.get("deterministic_block", {})
    summary_draft = latest_project_report.get("summary_draft", {})

    return {
        "project_id": project_profile.get("project_id", ""),
        "project_name": project_profile.get("project_name", ""),
        "project_type": project_profile.get("project_type", ""),
        "status": project_profile.get("status", ""),
        "client_name": project_profile.get("client", {}).get("name", ""),
        "pm_name": project_profile.get("pm", {}).get("name", ""),
        "jurisdiction": project_profile.get("jurisdiction", {}),
        "baseline_refs": baseline_lock.get("baseline_refs", {}),
        "workflow": {
            "workflow_status": workflow_snapshot.get("workflow_status", ""),
            "phase_count": workflow_snapshot.get("phase_count", 0),
            "current_phase_id": workflow_snapshot.get("current_phase_id", ""),
        },
        "latest_report": {
            "report_id": latest_project_report.get("report_id", ""),
            "report_status": latest_project_report.get("report_status", ""),
            "reporting_period_label": latest_project_report.get("reporting_period_label", ""),
            "headline": summary_draft.get("headline", ""),
            "bullets": list(summary_draft.get("bullets", [])),
        },
        "report_metrics": {
            "approved_change_total_amount": deterministic_block.get("change", {}).get(
                "approved_change_total_amount", 0.0
            ),
            "compliance_blocking": deterministic_block.get("compliance", {}).get(
                "blocking", False
            ),
            "conflict_count": deterministic_block.get("router", {}).get(
                "conflict_count", 0
            ),
            "open_or_monitoring_risks": deterministic_block.get("risk", {}).get(
                "open_or_monitoring_count", 0
            ),
        },
    }
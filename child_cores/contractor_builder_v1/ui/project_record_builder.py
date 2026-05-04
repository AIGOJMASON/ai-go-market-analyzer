"""
Project record builder for contractor_builder_v1.

This module shapes project artifacts into read-only project record views suitable
for UI rendering.

It supports:
- Stage 1 created-project view
- Stage 2 persistent project-record view
- Stage 5 change-governance visibility when change data is present
"""

from __future__ import annotations

from typing import Any, Dict, List


def _normalize_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return list(value)
    return []


def build_project_record_view(
    *,
    project_profile: Dict[str, Any],
    baseline_lock: Dict[str, Any],
    receipt_paths: Dict[str, Any],
    artifact_paths: Dict[str, str],
) -> Dict[str, Any]:
    client = dict(project_profile.get("client", {}))
    pm = dict(project_profile.get("pm", {}))
    jurisdiction = dict(project_profile.get("jurisdiction", {}))
    baseline_refs = dict(baseline_lock.get("baseline_refs", {}))

    return {
        "identity_panel": {
            "project_id": project_profile.get("project_id", ""),
            "project_name": project_profile.get("project_name", ""),
            "project_type": project_profile.get("project_type", ""),
            "status": project_profile.get("status", ""),
            "client_name": client.get("name", ""),
            "client_contact": client.get("contact", ""),
            "pm_name": pm.get("name", ""),
            "pm_contact": pm.get("contact", ""),
            "site_address": project_profile.get("site_address", ""),
            "portfolio_id": project_profile.get("portfolio_id", ""),
            "jurisdiction": jurisdiction,
        },
        "baseline_panel": {
            "lock_status": baseline_lock.get("lock_status", ""),
            "locked_at": baseline_lock.get("locked_at", ""),
            "schedule_baseline_id": baseline_refs.get("schedule_baseline_id", ""),
            "budget_baseline_id": baseline_refs.get("budget_baseline_id", ""),
            "compliance_snapshot_id": baseline_refs.get("compliance_snapshot_id", ""),
            "oracle_snapshot_id": baseline_refs.get("oracle_snapshot_id", ""),
            "exposure_profile_id": baseline_refs.get("exposure_profile_id", ""),
        },
        "receipts_panel": {
            "global_receipts": dict(receipt_paths.get("global_receipts", {})),
            "project_receipts": dict(receipt_paths.get("project_receipts", {})),
        },
        "artifacts_panel": {
            "project_profile_path": artifact_paths.get("project_profile_path", ""),
            "baseline_lock_path": artifact_paths.get("baseline_lock_path", ""),
        },
        "next_actions": [
            "Review the created project record.",
            "Continue to workflow setup when Stage 2 begins.",
            "Use the live dashboard only after project setup artifacts exist.",
        ],
    }


def build_persistent_project_record_view(
    *,
    project_record: Dict[str, Any],
) -> Dict[str, Any]:
    project_profile = _normalize_mapping(project_record.get("project_profile", {}))
    baseline_lock = _normalize_mapping(project_record.get("baseline_lock", {}))
    receipt_index = _normalize_list(project_record.get("receipt_index", []))
    documents_index = _normalize_list(project_record.get("documents_index", []))
    signoff_history = _normalize_list(project_record.get("signoff_history", []))
    change_index = _normalize_list(project_record.get("change_index", []))
    artifact_paths = _normalize_mapping(project_record.get("artifact_paths", {}))

    client = dict(project_profile.get("client", {}))
    pm = dict(project_profile.get("pm", {}))
    jurisdiction = dict(project_profile.get("jurisdiction", {}))
    baseline_refs = dict(baseline_lock.get("baseline_refs", {}))

    latest_receipts = receipt_index[:10]
    latest_signoffs = list(reversed(signoff_history[-10:]))

    blocking_change_items = [
        item for item in change_index
        if isinstance(item, dict) and bool(item.get("is_blocking_unresolved", False))
    ]
    latest_changes = list(reversed(change_index[-10:]))

    return {
        "summary_panel": {
            "project_id": project_profile.get("project_id", ""),
            "project_name": project_profile.get("project_name", ""),
            "project_type": project_profile.get("project_type", ""),
            "status": project_profile.get("status", ""),
            "receipt_count": len(receipt_index),
            "document_count": len(documents_index),
            "signoff_count": len(signoff_history),
            "change_count": len(change_index),
            "blocking_unresolved_change_count": len(blocking_change_items),
            "change_blocking": len(blocking_change_items) > 0,
        },
        "identity_panel": {
            "project_id": project_profile.get("project_id", ""),
            "project_name": project_profile.get("project_name", ""),
            "project_type": project_profile.get("project_type", ""),
            "status": project_profile.get("status", ""),
            "project_description": project_profile.get("project_description", ""),
            "client_name": client.get("name", ""),
            "client_contact": client.get("contact", ""),
            "pm_name": pm.get("name", ""),
            "pm_contact": pm.get("contact", ""),
            "site_address": project_profile.get("site_address", ""),
            "portfolio_id": project_profile.get("portfolio_id", ""),
            "jurisdiction": jurisdiction,
        },
        "baseline_panel": {
            "lock_status": baseline_lock.get("lock_status", ""),
            "locked_at": baseline_lock.get("locked_at", ""),
            "schedule_baseline_id": baseline_refs.get("schedule_baseline_id", ""),
            "budget_baseline_id": baseline_refs.get("budget_baseline_id", ""),
            "compliance_snapshot_id": baseline_refs.get("compliance_snapshot_id", ""),
            "oracle_snapshot_id": baseline_refs.get("oracle_snapshot_id", ""),
            "exposure_profile_id": baseline_refs.get("exposure_profile_id", ""),
        },
        "receipts_panel": {
            "receipt_count": len(receipt_index),
            "latest_receipts": latest_receipts,
        },
        "documents_panel": {
            "document_count": len(documents_index),
            "items": documents_index,
        },
        "signoff_history_panel": {
            "signoff_count": len(signoff_history),
            "items": latest_signoffs,
        },
        "changes_panel": {
            "change_count": len(change_index),
            "blocking_unresolved_change_count": len(blocking_change_items),
            "blocking_items": blocking_change_items[:10],
            "latest_items": latest_changes,
        },
        "artifacts_panel": {
            "project_root": project_record.get("project_root", ""),
            "project_profile_path": artifact_paths.get("project_profile_path", ""),
            "baseline_lock_path": artifact_paths.get("baseline_lock_path", ""),
            "signoff_history_path": artifact_paths.get("signoff_history_path", ""),
            "change_packets_path": artifact_paths.get("change_packets_path", ""),
            "change_signoff_status_path": artifact_paths.get("change_signoff_status_path", ""),
        },
    }
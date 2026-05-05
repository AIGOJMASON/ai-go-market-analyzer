"""
Identity helpers for contractor_builder_v1.

This module provides canonical ID generation for shared contractor-family entities.
The goal is consistency, traceability, and lawful cross-module references.
"""

from __future__ import annotations

from datetime import UTC, datetime
from secrets import token_hex
from typing import Optional


def _utc_timestamp_compact() -> str:
    """
    Return a compact UTC timestamp suitable for IDs.
    Example: 20260413T153045Z
    """
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _normalize_slug(value: str) -> str:
    """
    Normalize a freeform string into a safe slug segment.
    """
    cleaned = []
    for char in value.strip().lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "-", "_", "/", "."}:
            cleaned.append("_")
    slug = "".join(cleaned)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "unknown"


def _build_id(prefix: str, scope: Optional[str] = None, suffix_bytes: int = 4) -> str:
    """
    Build a canonical ID using:
    prefix + optional normalized scope + compact UTC timestamp + random suffix
    """
    parts = [prefix]
    if scope:
        parts.append(_normalize_slug(scope))
    parts.append(_utc_timestamp_compact())
    parts.append(token_hex(suffix_bytes))
    return "-".join(parts)


def build_project_id(project_name: str) -> str:
    return _build_id("project", project_name)


def build_phase_id(project_id: str, phase_name: str) -> str:
    return _build_id("phase", f"{project_id}_{phase_name}")


def build_change_packet_id(project_id: str, phase_id: str) -> str:
    return _build_id("change", f"{project_id}_{phase_id}")


def build_decision_id(project_id: str, decision_type: str) -> str:
    return _build_id("decision", f"{project_id}_{decision_type}")


def build_risk_id(project_id: str, category: str) -> str:
    return _build_id("risk", f"{project_id}_{category}")


def build_snapshot_id(jurisdiction_id: str, code_set_label: str) -> str:
    return _build_id("snapshot", f"{jurisdiction_id}_{code_set_label}")


def build_report_id(project_or_portfolio_id: str, report_type: str) -> str:
    return _build_id("report", f"{project_or_portfolio_id}_{report_type}")


def build_receipt_id(module_id: str, event_type: str) -> str:
    return _build_id("receipt", f"{module_id}_{event_type}")
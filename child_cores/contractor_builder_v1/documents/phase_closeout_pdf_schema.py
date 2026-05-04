"""
Phase closeout PDF schema for contractor_builder_v1.

This module defines the canonical structured metadata for a generated
phase closeout PDF artifact.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List


PHASE_CLOSEOUT_PDF_SCHEMA_VERSION = "v1"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_phase_closeout_pdf_artifact(
    *,
    artifact_id: str,
    project_id: str,
    phase_id: str,
    phase_name: str,
    pdf_path: str,
    pdf_hash: str,
    generated_at: str | None = None,
    version: int = 1,
) -> Dict[str, Any]:
    return {
        "schema_version": PHASE_CLOSEOUT_PDF_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "project_id": project_id,
        "phase_id": phase_id,
        "phase_name": phase_name,
        "pdf_path": pdf_path,
        "pdf_hash": pdf_hash,
        "generated_at": generated_at or _utc_now_iso(),
        "version": version,
    }


def validate_phase_closeout_pdf_artifact(artifact: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required_fields = [
        "artifact_id",
        "project_id",
        "phase_id",
        "phase_name",
        "pdf_path",
        "pdf_hash",
        "generated_at",
        "version",
    ]
    for field in required_fields:
        if field not in artifact:
            errors.append(f"Missing required PDF artifact field: {field}")

    if not artifact.get("artifact_id"):
        errors.append("artifact_id may not be empty")
    if not artifact.get("project_id"):
        errors.append("project_id may not be empty")
    if not artifact.get("phase_id"):
        errors.append("phase_id may not be empty")
    if not artifact.get("pdf_path"):
        errors.append("pdf_path may not be empty")
    if not artifact.get("pdf_hash"):
        errors.append("pdf_hash may not be empty")

    version = artifact.get("version")
    try:
        if int(version) < 1:
            errors.append("version must be >= 1")
    except Exception:
        errors.append("version must be an integer")

    return errors
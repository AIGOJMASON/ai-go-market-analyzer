from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_document_record",
        "mutation_class": "contractor_document_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_metadata(project_id: str, phase_id: str) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": "build_phase_closeout_pdf",
        "child_core_id": "contractor_builder_v1",
        "layer": "documents.phase_closeout_pdf_builder",
        "project_id": str(project_id or "").strip(),
        "phase_id": str(phase_id or "").strip(),
    }


def build_phase_closeout_pdf(
    *,
    project_id: str,
    phase_id: str,
    base_path: str,
    phase_name: str | None = None,
) -> dict:
    clean_project_id = str(project_id or "").strip()
    clean_phase_id = str(phase_id or "").strip()

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_phase_id:
        raise ValueError("phase_id is required")

    timestamp = int(time.time())
    filename = f"phase_closeout_{timestamp}.txt"
    file_path = Path(base_path) / filename

    content = (
        "AI_GO Contractor Phase Closeout\n"
        f"Project ID: {clean_project_id}\n"
        f"Phase ID: {clean_phase_id}\n"
        f"Phase Name: {phase_name or clean_phase_id}\n"
        f"Generated At: {timestamp}\n"
    )

    payload = {
        "artifact_type": "contractor_phase_closeout_document",
        "artifact_version": "northstar_document_v1",
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "phase_name": phase_name or clean_phase_id,
        "content": content,
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(clean_project_id, clean_phase_id),
        "sealed": True,
    }

    governed_write_json(
        path=file_path,
        payload=payload,
        mutation_class="contractor_document_persistence",
        persistence_type="contractor_document_record",
        authority_metadata=_authority_metadata(clean_project_id, clean_phase_id),
    )

    pdf_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    artifact_id = f"phase-closeout-{clean_phase_id}-{timestamp}"

    return {
        "artifact_id": artifact_id,
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "phase_name": phase_name or clean_phase_id,
        "pdf_path": str(file_path),
        "pdf_hash": pdf_hash,
        "generated_at": str(timestamp),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(clean_project_id, clean_phase_id),
        "sealed": True,
    }
# AI_GO/child_cores/contractor_builder_v1/governance/project_receipt_copy.py

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from AI_GO.core.receipts.receipt_writer import write_contractor_receipt


def write_project_receipt_copy(
    *,
    project_id: str,
    module_name: str,
    receipt: Dict[str, Any],
) -> Path:
    """
    Compatibility wrapper.

    Old callers pass raw receipts before receipt_id/integrity enrichment.
    The canonical receipt writer now handles:
    - receipt_id
    - integrity hash
    - short filename
    - parent directories
    - project-local receipt copy
    """
    event_type = str(receipt.get("event_type", "project_receipt_copy")).strip()

    result = write_contractor_receipt(
        module_name=module_name,
        event_type=event_type,
        receipt=receipt,
        project_id=project_id,
        write_project_copy=True,
    )

    project_path = result.get("project_path")
    if not project_path:
        raise ValueError("project receipt copy was not written")

    return Path(project_path)
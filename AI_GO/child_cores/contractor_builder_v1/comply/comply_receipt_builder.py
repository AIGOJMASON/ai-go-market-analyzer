# AI_GO/child_cores/contractor_builder_v1/comply/comply_receipt_builder.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from AI_GO.core.receipts.receipt_writer import write_contractor_receipt
except ModuleNotFoundError:
    from core.receipts.receipt_writer import write_contractor_receipt


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_comply_receipt",
        "mutation_class": "contractor_comply_receipt_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    event_type: str,
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "comply.comply_receipt_builder",
        "project_id": str(project_id or "").strip(),
        "event_type": str(event_type or "").strip(),
    }


def build_compliance_receipt(
    *,
    project_id: str,
    snapshot: Dict[str, Any] | None = None,
    event_type: str = "create_compliance_snapshot",
    artifact_path: str = "runtime://comply/snapshot",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build the canonical compliance receipt.

    Preserves the original base-code function used by contractor_comply_api.
    """
    clean_project_id = _required(project_id, "project_id")
    clean_event_type = _required(event_type, "event_type")
    clean_artifact_path = _required(artifact_path, "artifact_path")

    return {
        "module_id": "comply",
        "event_type": clean_event_type,
        "generated_at": _utc_now_iso(),
        "project_id": clean_project_id,
        "artifact_path": clean_artifact_path,
        "snapshot": dict(snapshot or {}),
        "details": dict(details or {}),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(
            operation="build_compliance_receipt",
            project_id=clean_project_id,
            event_type=clean_event_type,
        ),
        "sealed": True,
    }


def build_comply_receipt(
    *,
    event_type: str,
    project_id: str,
    artifact_path: str = "runtime://comply/snapshot",
    details: Optional[Dict[str, Any]] = None,
    snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compatibility alias expected by comply_executor.
    """
    return build_compliance_receipt(
        project_id=project_id,
        snapshot=snapshot or {},
        event_type=event_type,
        artifact_path=artifact_path,
        details=details,
    )


def write_compliance_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    """
    Persist a compliance receipt through the governed contractor receipt writer.
    """
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be a dict")

    payload = dict(receipt)
    event_type = str(payload.get("event_type", "compliance_event")).strip() or "compliance_event"
    project_id = str(payload.get("project_id", "")).strip()

    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(
        operation="write_compliance_receipt",
        project_id=project_id,
        event_type=event_type,
    )
    payload["sealed"] = True

    result = write_contractor_receipt(
        module_name="comply",
        event_type=event_type,
        receipt=payload,
        project_id=project_id or None,
        write_project_copy=False,
    )

    return Path(result["global_path"])


def write_comply_receipt(
    receipt: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    """
    Compatibility alias expected by comply_executor.
    """
    return write_compliance_receipt(receipt, create_dirs=create_dirs)
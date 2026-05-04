from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


RECEIPT_VERSION = "northstar_router_receipt_v1"
RECEIPT_ROOT = state_root() / "contractor_builder_v1" / "receipts" / "router"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_router_receipt",
        "mutation_class": "contractor_router_receipt_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_router_receipt_builder",
        "immutable_record": True,
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
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
        "layer": "router.router_receipt_builder",
        "project_id": _safe_str(project_id),
        "event_type": _safe_str(event_type),
    }


def build_router_receipt(
    *,
    event_type: str,
    project_id: str,
    artifact_path: str = "",
    actor: str = "system",
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    clean_event_type = _safe_str(event_type)
    clean_project_id = _safe_str(project_id)

    if not clean_event_type:
        raise ValueError("event_type is required")
    if not clean_project_id:
        raise ValueError("project_id is required")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt_id = f"receipt-router-{clean_event_type}-{timestamp}-{uuid4().hex[:8]}"

    return {
        "receipt_id": receipt_id,
        "receipt_version": RECEIPT_VERSION,
        "module_id": "router",
        "event_type": clean_event_type,
        "generated_at": _utc_now_iso(),
        "project_id": clean_project_id,
        "artifact_path": _safe_str(artifact_path),
        "actor": _safe_str(actor) or "system",
        "details": dict(details or {}),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "authority_metadata": _authority_metadata(
            operation="build_router_receipt",
            project_id=clean_project_id,
            event_type=clean_event_type,
        ),
        "sealed": True,
    }


def write_router_receipt(receipt: Dict[str, Any]) -> Path:
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be a dict")

    receipt_id = _safe_str(receipt.get("receipt_id"))
    project_id = _safe_str(receipt.get("project_id"))
    event_type = _safe_str(receipt.get("event_type"))

    if not receipt_id:
        raise ValueError("receipt_id is required")
    if not project_id:
        raise ValueError("project_id is required")

    payload = dict(receipt)
    payload["classification"] = _classification_block()
    payload["authority"] = _authority_block()
    payload["authority_metadata"] = _authority_metadata(
        operation="write_router_receipt",
        project_id=project_id,
        event_type=event_type,
    )
    payload["sealed"] = True

    path = RECEIPT_ROOT / f"{receipt_id}.json"

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="contractor_router_receipt_persistence",
        persistence_type="contractor_router_receipt",
        authority_metadata=payload["authority_metadata"],
    )

    return path
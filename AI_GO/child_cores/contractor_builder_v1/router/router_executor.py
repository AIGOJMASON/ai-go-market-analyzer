from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.router.router_receipt_builder import (
    build_router_receipt,
    write_router_receipt,
)
from AI_GO.child_cores.contractor_builder_v1.router.schedule_block_runtime import (
    upsert_schedule_blocks,
)


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not bool((execution_gate or {}).get("allowed") is True):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "message": "Router executor refused to write because execution_gate.allowed is not true.",
                "execution_gate": execution_gate,
            },
        )


def execute_persist_schedule_blocks(
    *,
    payload: Dict[str, Any],
    execution_gate: Dict[str, Any],
) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    project_id = str(payload.get("project_id", "")).strip()
    blocks: List[Dict[str, Any]] = list(payload.get("blocks", []))
    actor = str(payload.get("actor", "router_executor")).strip() or "router_executor"

    output_path = upsert_schedule_blocks(
        project_id=project_id,
        blocks=blocks,
    )

    receipt = build_router_receipt(
        event_type="store_schedule_blocks",
        project_id=project_id,
        artifact_path=str(output_path),
        actor=actor,
        details={
            "block_count": len(blocks),
        },
    )
    receipt_path = write_router_receipt(receipt)

    return {
        "status": "stored",
        "project_id": project_id,
        "artifact_path": str(output_path),
        "receipt_path": str(receipt_path),
        "block_count": len(blocks),
    }
from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from AI_GO.child_cores.contractor_builder_v1.comply.comply_receipt_builder import (
    build_comply_receipt,
    write_comply_receipt,
)


def _classification_block() -> Dict[str, Any]:
    return {
        "mutation_class": "contractor_comply_persistence",
        "persistence_type": "contractor_compliance_record",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_metadata(project_id: str, operation: str) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "comply.comply_executor",
        "project_id": str(project_id or "").strip(),
    }


def _assert_gate(execution_gate: Dict[str, Any]) -> None:
    if not bool((execution_gate or {}).get("allowed") is True):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "execution_gate_blocked",
                "execution_gate": execution_gate,
            },
        )


def _run_inline_compliance_runtime(*, project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "ok",
        "project_id": project_id,
        "artifact_path": "",
        "details": dict(payload or {}),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(project_id, "run_inline_compliance_runtime"),
        "sealed": True,
    }


def execute_compliance(*, payload: Dict[str, Any], execution_gate: Dict[str, Any]) -> Dict[str, Any]:
    _assert_gate(execution_gate)

    project_id = str(payload.get("project_id", "")).strip()
    if not project_id:
        raise ValueError("project_id is required")

    result = _run_inline_compliance_runtime(
        project_id=project_id,
        payload=payload.get("payload", {}) if isinstance(payload.get("payload", {}), dict) else {},
    )

    receipt = build_comply_receipt(
        event_type="run_compliance",
        project_id=project_id,
        artifact_path=str(result.get("artifact_path", "")),
        details={
            **dict(result),
            "mutation_class": "contractor_comply_persistence",
            "persistence_type": "contractor_compliance_record",
            "authority_metadata": _authority_metadata(project_id, "execute_compliance"),
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "advisory_only": False,
        },
    )

    receipt_path = write_comply_receipt(receipt)

    return {
        "status": "completed",
        "project_id": project_id,
        "artifact_path": result.get("artifact_path"),
        "receipt_path": str(receipt_path),
        "compliance_result": result,
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(project_id, "execute_compliance"),
        "sealed": True,
    }


def execute_compliance_check(*, payload: Dict[str, Any], execution_gate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward-compatible public contract expected by comply_service.
    """
    return execute_compliance(payload=payload, execution_gate=execution_gate)
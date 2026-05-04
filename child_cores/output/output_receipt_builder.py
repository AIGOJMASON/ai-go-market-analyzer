from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _output_id(runtime_id: str, target_core: str) -> str:
    core_slug = target_core.upper().replace("-", "_")
    return f"OUTPUT-{core_slug}-{runtime_id}"


def build_output_artifact(
    *,
    runtime_receipt: Dict[str, Any],
    output_surface: str,
    payload: Dict[str, Any] | None = None,
    payload_ref: str | None = None,
) -> Dict[str, Any]:
    runtime_id = runtime_receipt["runtime_id"]
    target_core = runtime_receipt["target_core"]
    output_id = _output_id(runtime_id, target_core)

    artifact: Dict[str, Any] = {
        "artifact_type": "output_artifact",
        "stage": "stage23_child_core_output",
        "output_id": output_id,
        "source_runtime_id": runtime_id,
        "source_ingress_id": runtime_receipt["source_ingress_id"],
        "source_dispatch_id": runtime_receipt["source_dispatch_id"],
        "source_decision_id": runtime_receipt["source_decision_id"],
        "target_core": target_core,
        "output_surface": output_surface,
        "output_status": "constructed",
        "timestamp": _utc_now_iso(),
    }

    if payload is not None:
        artifact["payload"] = payload
    if payload_ref is not None:
        artifact["payload_ref"] = payload_ref

    return artifact


def build_output_receipt(
    *,
    output_artifact: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "output_receipt",
        "stage": "stage23_child_core_output",
        "output_id": output_artifact["output_id"],
        "source_runtime_id": output_artifact["source_runtime_id"],
        "target_core": output_artifact["target_core"],
        "output_surface": output_artifact["output_surface"],
        "output_artifact_ref": output_artifact["output_id"],
        "output_status": output_artifact["output_status"],
        "timestamp": _utc_now_iso(),
    }


def build_output_failure_receipt(
    *,
    reason: str,
    runtime_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "output_failure_receipt",
        "stage": "stage23_child_core_output",
        "runtime_id": runtime_receipt.get("runtime_id"),
        "target_core": runtime_receipt.get("target_core"),
        "reason": reason,
        "timestamp": _utc_now_iso(),
        "propagation_status": "terminated",
    }
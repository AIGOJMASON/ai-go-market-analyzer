from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_runtime_receipt(
    ingress_receipt: Dict[str, Any],
    execution_surface: str,
    result_ref: str | None = None,
) -> Dict[str, Any]:
    """
    Build a receipt for successful runtime start / bounded execution.
    """
    runtime_id = f"RUNTIME-{uuid4()}"

    receipt = {
        "artifact_type": "runtime_receipt",
        "runtime_id": runtime_id,
        "source_ingress_id": ingress_receipt["ingress_id"],
        "source_dispatch_id": ingress_receipt["source_dispatch_id"],
        "source_decision_id": ingress_receipt["source_decision_id"],
        "target_core": ingress_receipt["target_core"],
        "execution_surface": execution_surface,
        "runtime_status": "completed",
        "timestamp": utc_now_iso(),
    }

    if result_ref is not None:
        receipt["result_ref"] = result_ref

    return receipt


def build_runtime_failure_receipt(
    reason: str,
    ingress_receipt: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build a receipt for failed runtime validation or invocation.
    """
    ingress_id = None
    target_core = None

    if ingress_receipt is not None:
        ingress_id = ingress_receipt.get("ingress_id")
        target_core = ingress_receipt.get("target_core")

    return {
        "artifact_type": "runtime_failure_receipt",
        "stage": "CHILD_CORE_RUNTIME",
        "ingress_id": ingress_id,
        "target_core": target_core,
        "reason": reason,
        "propagation_status": "terminated",
        "timestamp": utc_now_iso(),
    }
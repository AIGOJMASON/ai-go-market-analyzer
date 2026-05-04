from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _review_id(output_id: str, target_core: str) -> str:
    core_slug = target_core.upper().replace("-", "_")
    return f"REVIEW-{core_slug}-{output_id}"


def build_output_disposition_receipt(
    *,
    output_artifact: Dict[str, Any],
    requested_target: str,
    selected_target: str,
    disposition_status: str = "routed",
) -> Dict[str, Any]:
    review_id = _review_id(output_artifact["output_id"], output_artifact["target_core"])

    return {
        "artifact_type": "output_disposition_receipt",
        "stage": "stage24_child_core_review",
        "review_id": review_id,
        "source_output_id": output_artifact["output_id"],
        "source_runtime_id": output_artifact["source_runtime_id"],
        "target_core": output_artifact["target_core"],
        "requested_target": requested_target,
        "selected_target": selected_target,
        "disposition_status": disposition_status,
        "timestamp": _utc_now_iso(),
    }


def build_review_hold_receipt(
    *,
    output_artifact: Dict[str, Any],
    requested_target: str,
    reason: str,
) -> Dict[str, Any]:
    review_id = _review_id(output_artifact["output_id"], output_artifact["target_core"])

    return {
        "artifact_type": "review_hold_receipt",
        "stage": "stage24_child_core_review",
        "review_id": review_id,
        "source_output_id": output_artifact["output_id"],
        "target_core": output_artifact["target_core"],
        "requested_target": requested_target,
        "reason": reason,
        "timestamp": _utc_now_iso(),
        "propagation_status": "held",
    }


def build_review_failure_receipt(
    *,
    reason: str,
    output_artifact: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "review_failure_receipt",
        "stage": "stage24_child_core_review",
        "output_id": output_artifact.get("output_id"),
        "target_core": output_artifact.get("target_core"),
        "reason": reason,
        "timestamp": _utc_now_iso(),
        "propagation_status": "terminated",
    }
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _watcher_id(review_id: str, target_core: str) -> str:
    core_slug = target_core.upper().replace("-", "_")
    return f"WATCHER-{core_slug}-{review_id}"


def build_watcher_result(
    *,
    disposition_receipt: Dict[str, Any],
    findings: Dict[str, Any] | None = None,
    findings_ref: str | None = None,
    watcher_status: str = "completed",
) -> Dict[str, Any]:
    review_id = disposition_receipt["review_id"]
    target_core = disposition_receipt["target_core"]
    watcher_id = _watcher_id(review_id, target_core)

    artifact: Dict[str, Any] = {
        "artifact_type": "watcher_result",
        "stage": "stage25_child_core_watcher",
        "watcher_id": watcher_id,
        "source_review_id": review_id,
        "source_output_id": disposition_receipt["source_output_id"],
        "source_runtime_id": disposition_receipt["source_runtime_id"],
        "target_core": target_core,
        "watcher_status": watcher_status,
        "timestamp": _utc_now_iso(),
    }

    if findings is not None:
        artifact["findings"] = findings
    if findings_ref is not None:
        artifact["findings_ref"] = findings_ref

    return artifact


def build_watcher_receipt(
    *,
    watcher_result: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "watcher_receipt",
        "stage": "stage25_child_core_watcher",
        "watcher_id": watcher_result["watcher_id"],
        "source_review_id": watcher_result["source_review_id"],
        "source_output_id": watcher_result["source_output_id"],
        "target_core": watcher_result["target_core"],
        "watcher_status": watcher_result["watcher_status"],
        "watcher_result_ref": watcher_result["watcher_id"],
        "timestamp": _utc_now_iso(),
    }


def build_watcher_failure_receipt(
    *,
    reason: str,
    disposition_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "watcher_failure_receipt",
        "stage": "stage25_child_core_watcher",
        "review_id": disposition_receipt.get("review_id"),
        "target_core": disposition_receipt.get("target_core"),
        "reason": reason,
        "timestamp": _utc_now_iso(),
        "propagation_status": "terminated",
    }
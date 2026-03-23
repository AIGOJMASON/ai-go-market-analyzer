from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_receipt_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


def build_continuity_intake_receipt(
    *,
    target_core: str,
    continuity_scope: str,
    admission_basis: str,
    watcher_receipt_ref: str,
    output_disposition_ref: str,
    runtime_ref: str,
    policy_version: str,
    receipt_ref: Optional[str] = None,
) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    intake_id = _new_receipt_id("CONTINUITY-INTAKE")
    return {
        "receipt_type": "continuity_intake_receipt",
        "intake_id": intake_id,
        "target_core": target_core,
        "continuity_scope": continuity_scope,
        "admission_basis": admission_basis,
        "watcher_receipt_ref": watcher_receipt_ref,
        "output_disposition_ref": output_disposition_ref,
        "runtime_ref": runtime_ref,
        "policy_version": policy_version,
        "timestamp": timestamp,
        "next_target": "future_continuity_mutation_layer",
        "receipt_ref": receipt_ref,
    }


def build_continuity_hold_receipt(
    *,
    target_core: str,
    hold_reason: str,
    release_condition: str,
    watcher_receipt_ref: str,
    output_disposition_ref: str,
    runtime_ref: str,
    policy_version: str,
    review_window: Optional[str] = None,
    receipt_ref: Optional[str] = None,
) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    hold_id = _new_receipt_id("CONTINUITY-HOLD")
    return {
        "receipt_type": "continuity_hold_receipt",
        "hold_id": hold_id,
        "target_core": target_core,
        "hold_reason": hold_reason,
        "release_condition": release_condition,
        "review_window": review_window,
        "watcher_receipt_ref": watcher_receipt_ref,
        "output_disposition_ref": output_disposition_ref,
        "runtime_ref": runtime_ref,
        "policy_version": policy_version,
        "timestamp": timestamp,
        "receipt_ref": receipt_ref,
    }


def build_continuity_failure_receipt(
    *,
    target_core: Optional[str],
    rejection_code: str,
    rejection_reason: str,
    watcher_receipt_ref: Optional[str],
    output_disposition_ref: Optional[str],
    runtime_ref: Optional[str],
    policy_version: Optional[str],
    receipt_ref: Optional[str] = None,
) -> Dict[str, Any]:
    timestamp = utc_now_iso()
    failure_id = _new_receipt_id("CONTINUITY-FAILURE")
    return {
        "receipt_type": "continuity_failure_receipt",
        "failure_id": failure_id,
        "target_core": target_core,
        "rejection_code": rejection_code,
        "rejection_reason": rejection_reason,
        "watcher_receipt_ref": watcher_receipt_ref,
        "output_disposition_ref": output_disposition_ref,
        "runtime_ref": runtime_ref,
        "policy_version": policy_version,
        "timestamp": timestamp,
        "receipt_ref": receipt_ref,
    }
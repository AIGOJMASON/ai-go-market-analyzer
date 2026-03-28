from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_receipt_id(prefix: str, payload: Dict[str, Any]) -> str:
    digest = sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:12]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{digest}"


def build_qualification_receipt(record: Dict[str, Any]) -> Dict[str, Any]:
    receipt = {
        "artifact_type": "external_memory_qualification_receipt",
        "receipt_id": build_receipt_id("extmem_qual", record),
        "created_at": utc_timestamp(),
        "decision": record["decision"],
        "qualification_record_id": record["qualification_record_id"],
        "source_type": record["source_type"],
        "target_child_cores": record["target_child_cores"],
        "adjusted_weight": record["adjusted_weight"],
        "source_quality_weight": record["source_quality_weight"],
        "trust_class": record["trust_class"],
        "rejection_reason": record.get("rejection_reason"),
    }
    return receipt
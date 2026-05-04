from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def _ts() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_mutation_receipt(
    *,
    target_core: str,
    mutation_type: str,
    intake_id: str,
    upstream_policy_version: str,
    mutation_policy_version: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_mutation_receipt",
        "mutation_id": f"CMR-{uuid4().hex[:12].upper()}",
        "target_core": target_core,
        "mutation_type": mutation_type,
        "source_intake_id": intake_id,
        "upstream_policy_version": upstream_policy_version,
        "mutation_policy_version": mutation_policy_version,
        "timestamp": _ts(),
    }


def build_failure_receipt(
    *,
    target_core: Optional[str],
    code: str,
    reason: str,
    upstream_policy_version: Optional[str],
    mutation_policy_version: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_mutation_failure_receipt",
        "failure_id": f"CMF-{uuid4().hex[:12].upper()}",
        "target_core": target_core,
        "rejection_code": code,
        "reason": reason,
        "upstream_policy_version": upstream_policy_version,
        "mutation_policy_version": mutation_policy_version,
        "timestamp": _ts(),
    }
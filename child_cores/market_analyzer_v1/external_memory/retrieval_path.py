from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from AI_GO.EXTERNAL_MEMORY.retrieval.read_only_context import (
        build_external_memory_read_only_context,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.retrieval.read_only_context import (
        build_external_memory_read_only_context,
    )


def _clean_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def run_market_analyzer_external_memory_retrieval(
    requester_profile: str = "market_analyzer_reader",
    symbol: Optional[str] = None,
    sector: Optional[str] = None,
    trust_class: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 10,
    min_adjusted_weight: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Market Analyzer retrieval is read-only advisory context.

    It may inspect bounded persisted memory.
    It may not:
    - mutate runtime output
    - alter recommendation logic
    - alter PM influence
    - promote records
    - override governance
    """
    request: Dict[str, Any] = {
        "artifact_type": "external_memory_retrieval_request",
        "requester_profile": requester_profile,
        "target_child_core": "market_analyzer_v1",
        "limit": limit,
    }

    optional_filters = {
        "symbol": _clean_optional(symbol),
        "sector": _clean_optional(sector),
        "trust_class": _clean_optional(trust_class),
        "source_type": _clean_optional(source_type),
        "min_adjusted_weight": min_adjusted_weight,
    }

    for key, value in optional_filters.items():
        if value is not None:
            request[key] = value

    context = build_external_memory_read_only_context(request)

    artifact = {
        "artifact_type": "external_memory_retrieval_artifact",
        "status": context.get("retrieval_status", context.get("status", "failed")),
        "request_summary": context.get("request_summary", {}),
        "matched_count": context.get("matched_count", 0),
        "returned_count": context.get("returned_count", 0),
        "records": context.get("records", []),
        "authority": context.get("authority", {}),
        "sealed": True,
    }

    receipt = {
        "artifact_type": "external_memory_retrieval_receipt_reference",
        "receipt_id": context.get("retrieval_receipt_id", ""),
        "authority": context.get("authority", {}),
        "sealed": True,
    }

    return {
        "status": context.get("status", "failed"),
        "retrieval_context": context,
        "external_memory_panel": context.get("advisory_panel", {}),
        "retrieval_artifact": artifact,
        "retrieval_receipt": receipt,
        "artifact": artifact,
        "receipt": receipt,
        "authority": context.get("authority", {}),
    }
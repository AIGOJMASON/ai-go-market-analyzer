from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
        run_external_memory_retrieval,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
        run_external_memory_retrieval,
    )


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
    Market Analyzer retrieval should stay permissive enough to recover
    repeated symbol-level event history for downstream promotion/pattern logic.

    Intentionally minimal filter set:
    - requester_profile
    - target_child_core
    - limit
    - symbol

    This avoids over-constraining retrieval with fields that may vary across
    otherwise relevant historical records.
    """
    request = {
        "artifact_type": "external_memory_retrieval_request",
        "requester_profile": requester_profile,
        "target_child_core": "market_analyzer_v1",
        "limit": limit,
        "symbol": symbol,
    }

    result = run_external_memory_retrieval(request)

    if not isinstance(result, dict):
        return {
            "retrieval_artifact": None,
            "retrieval_receipt": None,
            "artifact": None,
            "receipt": None,
        }

    artifact = result.get("artifact") or result.get("retrieval_artifact")
    receipt = result.get("receipt") or result.get("retrieval_receipt")

    return {
        "retrieval_artifact": artifact,
        "retrieval_receipt": receipt,
        "artifact": artifact,
        "receipt": receipt,
    }
from __future__ import annotations

from typing import Any, Dict

from AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
    run_external_memory_retrieval,
)


def run_market_analyzer_external_memory_retrieval(
    limit: int = 10,
    source_type: str | None = None,
    trust_class: str | None = None,
    min_adjusted_weight: float | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    requester_profile: str = "market_analyzer_reader",
) -> Dict[str, Any]:
    request = {
        "artifact_type": "external_memory_retrieval_request",
        "requester_profile": requester_profile,
        "target_child_core": "market_analyzer_v1",
        "limit": limit,
        "source_type": source_type,
        "trust_class": trust_class,
        "min_adjusted_weight": min_adjusted_weight,
        "symbol": symbol,
        "sector": sector,
    }
    return run_external_memory_retrieval(request)
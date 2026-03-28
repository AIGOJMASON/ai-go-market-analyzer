from __future__ import annotations

from typing import Any, Dict

from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
    run_external_memory_promotion,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
    run_market_analyzer_external_memory_retrieval,
)


def run_market_analyzer_external_memory_promotion(
    limit: int = 10,
    source_type: str | None = None,
    trust_class: str | None = None,
    min_adjusted_weight: float | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    requester_profile: str = "market_analyzer_reader",
) -> Dict[str, Any]:
    retrieval_result = run_market_analyzer_external_memory_retrieval(
        limit=limit,
        source_type=source_type,
        trust_class=trust_class,
        min_adjusted_weight=min_adjusted_weight,
        symbol=symbol,
        sector=sector,
        requester_profile=requester_profile,
    )
    return run_external_memory_promotion(
        artifact=retrieval_result["artifact"] or {},
        receipt=retrieval_result["receipt"],
    )
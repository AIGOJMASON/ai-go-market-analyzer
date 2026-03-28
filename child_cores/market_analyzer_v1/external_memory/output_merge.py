from __future__ import annotations

from typing import Any, Dict

from AI_GO.EXTERNAL_MEMORY.output_merge.output_merge_runtime import (
    merge_external_memory_into_operator_output,
)
from AI_GO.child_cores.market_analyzer_v1.external_memory.return_path import (
    run_market_analyzer_external_memory_return_path,
)


def merge_market_analyzer_external_memory_output(
    operator_response: Dict[str, Any],
    limit: int = 10,
    source_type: str | None = None,
    trust_class: str | None = None,
    min_adjusted_weight: float | None = None,
    symbol: str | None = None,
    sector: str | None = None,
    requester_profile: str = "market_analyzer_reader",
) -> Dict[str, Any]:
    return_result = run_market_analyzer_external_memory_return_path(
        limit=limit,
        source_type=source_type,
        trust_class=trust_class,
        min_adjusted_weight=min_adjusted_weight,
        symbol=symbol,
        sector=sector,
        requester_profile=requester_profile,
    )
    return merge_external_memory_into_operator_output(
        operator_response=operator_response,
        return_packet=return_result["artifact"] or {},
        return_receipt=return_result["receipt"],
    )
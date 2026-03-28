from __future__ import annotations

from typing import Any, Dict

from AI_GO.EXTERNAL_MEMORY.pattern_aggregation import aggregate_pattern


def build_market_analyzer_pattern_context(
    promotion_artifact: Dict[str, Any],
    promotion_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    return aggregate_pattern(
        promotion_artifact=promotion_artifact,
        promotion_receipt=promotion_receipt,
    )
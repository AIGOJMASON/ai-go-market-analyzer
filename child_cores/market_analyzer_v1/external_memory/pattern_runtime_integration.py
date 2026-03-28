from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
        build_market_analyzer_pattern_context,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.return_path import (
        build_market_analyzer_return_packet,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
        build_market_analyzer_pattern_context,
    )
    from child_cores.market_analyzer_v1.external_memory.return_path import (
        build_market_analyzer_return_packet,
    )


def apply_external_memory_pattern_flow(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Live integration layer:

    result
    → extract promotion artifact
    → pattern aggregation
    → return path
    → attach advisory panel

    Fully non-mutating to core decision logic.
    """

    enriched = dict(result)

    promotion_artifact = enriched.get("external_memory_promotion_artifact")
    promotion_receipt = enriched.get("external_memory_promotion_receipt")

    if not promotion_artifact or not promotion_receipt:
        return enriched

    pattern_result = build_market_analyzer_pattern_context(
        promotion_artifact,
        promotion_receipt,
    )

    if pattern_result.get("status") != "ok":
        return enriched

    pattern_artifact = pattern_result["artifact"]
    pattern_receipt = pattern_result["receipt"]

    return_result = build_market_analyzer_return_packet(
        pattern_artifact,
        pattern_receipt,
    )

    if return_result.get("status") != "ok":
        return enriched

    return_artifact = return_result["artifact"]

    enriched["external_memory_pattern_panel"] = return_artifact.get(
        "external_memory_return_panel"
    )

    return enriched
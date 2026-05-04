# external_memory_projection.py
from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.promotion_path import (
        run_market_analyzer_external_memory_promotion,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
        build_market_analyzer_pattern_context,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.output_merge import (
        build_market_analyzer_external_memory_packet,
    )
except ImportError:
    from child_cores.market_analyzer_v1.external_memory.promotion_path import (
        run_market_analyzer_external_memory_promotion,
    )
    from child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
        build_market_analyzer_pattern_context,
    )
    from child_cores.market_analyzer_v1.external_memory.output_merge import (
        build_market_analyzer_external_memory_packet,
    )


def _empty_projection() -> Dict[str, Any]:
    return {
        "source_1_summary": {},
        "external_memory_packet": {},
    }


def build_external_memory_projection(symbol: str) -> Dict[str, Any]:
    normalized_symbol = str(symbol or "").strip().upper()
    if not normalized_symbol:
        return _empty_projection()

    promotion_result = run_market_analyzer_external_memory_promotion(
        symbol=normalized_symbol,
        limit=5,
    )
    if not isinstance(promotion_result, dict) or promotion_result.get("status") != "ok":
        return _empty_projection()

    artifact = promotion_result.get("artifact") or {}
    receipt = promotion_result.get("receipt") or {}

    source_1_summary: Dict[str, Any] = {
        "artifact_type": "market_analyzer_source_1_summary",
        "status": "ok",
        "promotion_artifact": artifact,
        "promotion_receipt": receipt,
    }

    pattern_result = build_market_analyzer_pattern_context(
        promotion_artifact=artifact,
        promotion_receipt=receipt,
    )
    if isinstance(pattern_result, dict) and pattern_result.get("status") == "ok":
        source_1_summary["pattern_artifact"] = pattern_result.get("artifact") or {}
        source_1_summary["pattern_receipt"] = pattern_result.get("receipt") or {}

    source_artifact = (
        source_1_summary.get("pattern_artifact")
        or source_1_summary.get("promotion_artifact")
        or {}
    )
    source_receipt = (
        source_1_summary.get("pattern_receipt")
        or source_1_summary.get("promotion_receipt")
        or {}
    )

    packet_result = build_market_analyzer_external_memory_packet(
        source_artifact=source_artifact,
        source_receipt=source_receipt,
    )
    if not isinstance(packet_result, dict) or packet_result.get("status") != "ok":
        return {
            "source_1_summary": source_1_summary,
            "external_memory_packet": {},
        }

    external_memory_packet = packet_result.get("external_memory_packet") or {}
    return {
        "source_1_summary": source_1_summary,
        "external_memory_packet": external_memory_packet if isinstance(external_memory_packet, dict) else {},
    }
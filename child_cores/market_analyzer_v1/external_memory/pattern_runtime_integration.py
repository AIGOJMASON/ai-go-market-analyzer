from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (
        build_market_analyzer_pattern_context,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.output_merge import (
        build_market_analyzer_external_memory_packet,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.pattern_aggregation import (  # type: ignore
        build_market_analyzer_pattern_context,
    )
    from child_cores.market_analyzer_v1.external_memory.output_merge import (  # type: ignore
        build_market_analyzer_external_memory_packet,
    )


def build_external_memory_bridge_packet(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the bounded External Memory bridge packet for pre-AI synthesis.

    Flow:
    result
    -> extract promotion artifact
    -> pattern aggregation
    -> return path
    -> emit external_memory_packet

    IMPORTANT
    - no operator/UI merge occurs here
    - no runtime mutation occurs here
    - this is a bridge-prep helper only
    """
    if not isinstance(result, dict):
        return {
            "status": "failed",
            "external_memory_packet": None,
            "receipt": {"failure_reason": "invalid_result_type"},
        }

    promotion_artifact = result.get("external_memory_promotion_artifact")
    promotion_receipt = result.get("external_memory_promotion_receipt")

    if not isinstance(promotion_artifact, dict) or not isinstance(promotion_receipt, dict):
        return {
            "status": "failed",
            "external_memory_packet": None,
            "receipt": {"failure_reason": "missing_promotion_artifact_or_receipt"},
        }

    pattern_result = build_market_analyzer_pattern_context(
        promotion_artifact,
        promotion_receipt,
    )

    source_artifact = promotion_artifact
    source_receipt = promotion_receipt

    if isinstance(pattern_result, dict) and pattern_result.get("status") == "ok":
        source_artifact = pattern_result.get("artifact") or source_artifact
        source_receipt = pattern_result.get("receipt") or source_receipt

    packet_result = build_market_analyzer_external_memory_packet(
        source_artifact=source_artifact,
        source_receipt=source_receipt,
    )

    if not isinstance(packet_result, dict) or packet_result.get("status") != "ok":
        return {
            "status": "failed",
            "external_memory_packet": None,
            "receipt": packet_result.get("receipt") if isinstance(packet_result, dict) else None,
        }

    return {
        "status": "ok",
        "external_memory_packet": packet_result.get("external_memory_packet"),
        "receipt": packet_result.get("receipt"),
    }


def apply_external_memory_pattern_flow(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Backward-compatible alias.

    Under the new architecture this returns the bridge packet instead of
    operator-visible merged output.
    """
    return build_external_memory_bridge_packet(result)
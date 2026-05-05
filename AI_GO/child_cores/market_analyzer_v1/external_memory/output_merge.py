from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.return_path import (
        build_market_analyzer_return_packet,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.return_path import (  # type: ignore
        build_market_analyzer_return_packet,
    )


def build_market_analyzer_external_memory_packet(
    source_artifact: Dict[str, Any],
    source_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the bounded External Memory egress packet.

    IMPORTANT
    - This file no longer merges anything into operator-visible output.
    - It stops at the lawful External Memory return packet.
    - The packet is intended for API-side synthesis before the AI call.
    """
    return_result = build_market_analyzer_return_packet(
        source_artifact=source_artifact,
        source_receipt=source_receipt,
    )

    if return_result.get("status") != "ok":
        return {
            "status": "failed",
            "external_memory_packet": None,
            "receipt": return_result.get("receipt"),
        }

    return {
        "status": "ok",
        "external_memory_packet": return_result.get("artifact"),
        "receipt": return_result.get("receipt"),
    }


def merge_market_analyzer_external_memory_output(
    operator_response: Dict[str, Any],
    source_artifact: Dict[str, Any],
    source_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper.

    Older callers may still import this symbol. Under the new architecture,
    the function returns an External Memory packet result instead of mutating
    or merging into operator output.
    """
    _ = operator_response
    return build_market_analyzer_external_memory_packet(
        source_artifact=source_artifact,
        source_receipt=source_receipt,
    )
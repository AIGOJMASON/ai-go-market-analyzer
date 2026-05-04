from __future__ import annotations

from typing import Any, Dict

try:
    from AI_GO.EXTERNAL_MEMORY.promotion.promotion_runtime import (
        run_external_memory_promotion,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.promotion.promotion_runtime import (
        run_external_memory_promotion,
    )


def run_market_analyzer_external_memory_promotion(
    retrieval_artifact: Dict[str, Any],
    retrieval_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Market Analyzer promotion is advisory only.

    It may:
    - evaluate retrieved memory as reusable advisory signal
    - return a promotion artifact and receipt

    It may not:
    - mutate Market Analyzer runtime
    - change recommendations
    - change PM strategy
    - execute
    - override governance
    """
    result = run_external_memory_promotion(
        artifact=retrieval_artifact,
        receipt=retrieval_receipt,
    )

    promotion_artifact = result.get("promotion_artifact") or result.get("artifact") or {}
    promotion_receipt = result.get("promotion_receipt") or result.get("receipt") or {}

    return {
        "status": result.get("status", "rejected"),
        "decision": result.get("decision") or promotion_artifact.get("promotion_decision", "reject"),
        "promotion_artifact": promotion_artifact,
        "promotion_receipt": promotion_receipt,
        "external_memory_promotion_panel": {
            "visible": True,
            "source": "external_memory",
            "mode": "promotion_advisory",
            "advisory_only": True,
            "promotion_decision": promotion_artifact.get("promotion_decision", "reject"),
            "promotion_score": promotion_artifact.get("promotion_score"),
            "record_count": promotion_artifact.get("record_count", 0),
            "reusable_advisory_signal": promotion_artifact.get("reusable_advisory_signal", False),
            "summary": "External Memory promotion is advisory pattern context only.",
        },
        "authority": promotion_artifact.get("authority", {}),
    }
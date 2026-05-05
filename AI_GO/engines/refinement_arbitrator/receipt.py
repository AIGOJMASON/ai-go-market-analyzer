from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_arbitration_id() -> str:
    return f"RA-{uuid.uuid4().hex[:12].upper()}"


def build_receipt(
    *,
    arbitration_id: str,
    source_packet_id: str,
    recommended_action: str,
    reasoning_weight: float,
    human_tempering_weight: float,
    child_core_fit_scores: Dict[str, float],
    composite_weight: float,
    engine_invocations: List[Dict[str, Any]],
    target_child_core: Optional[str],
    threshold_band: str,
    justification_summary: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "arbitration_receipt",
        "arbitration_id": arbitration_id,
        "source_packet_id": source_packet_id,
        "issuing_layer": "REFINEMENT_ARBITRATOR",
        "recommended_action": recommended_action,
        "reasoning_weight": reasoning_weight,
        "human_tempering_weight": human_tempering_weight,
        "child_core_fit_scores": child_core_fit_scores,
        "composite_weight": composite_weight,
        "engine_invocations": engine_invocations,
        "target_child_core": target_child_core,
        "threshold_band": threshold_band,
        "justification_summary": justification_summary,
        "timestamp": utc_now(),
    }
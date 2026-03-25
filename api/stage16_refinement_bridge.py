from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.api.quarantine_retrieval import list_quarantined_closeouts
from AI_GO.core.runtime.refinement.refinement_arbitrator import (
    build_refinement_arbitrator_packet_from_runtime,
)


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def build_stage16_refinement_for_market_analyzer(
    *,
    market_panel: Dict[str, Any],
    historical_analog_panel: Dict[str, Any],
    governance_panel: Dict[str, Any],
) -> Dict[str, Any]:
    quarantine_index = list_quarantined_closeouts(limit=200, offset=0)
    quarantine_items = _safe_list(quarantine_index.get("items"))

    return build_refinement_arbitrator_packet_from_runtime(
        core_id="market_analyzer_v1",
        market_panel=market_panel,
        historical_analog_panel=historical_analog_panel,
        governance_panel=governance_panel,
        quarantine_items=quarantine_items,
    )
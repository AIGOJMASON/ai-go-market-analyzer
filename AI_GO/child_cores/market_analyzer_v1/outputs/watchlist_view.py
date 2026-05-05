from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _candidate_watch_row(candidate: Dict[str, Any]) -> Dict[str, Any]:
    item = deepcopy(candidate)
    return {
        "symbol": item.get("symbol"),
        "sector": item.get("sector"),
        "liquidity": item.get("liquidity"),
        "necessity_filter_pass": item.get("necessity_filter_pass", False),
        "stabilization": item.get("stabilization", False),
        "reclaim": item.get("reclaim", False),
        "confirmation": item.get("confirmation", False),
    }


def build_watchlist_view(necessity_filtered_candidate_set: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render the filtered watchlist panel.
    """
    record = deepcopy(necessity_filtered_candidate_set)
    filtered_candidates = record.get("filtered_candidates", [])

    rows: List[Dict[str, Any]] = [_candidate_watch_row(candidate) for candidate in filtered_candidates]

    return {
        "panel": "watchlist",
        "core_id": "market_analyzer_v1",
        "artifact_type": "watchlist_view",
        "count": len(rows),
        "items": rows,
        "filtered_count": record.get("filtered_count", 0),
        "rejected_count": record.get("rejected_count", 0),
        "allowed_sectors": deepcopy(record.get("allowed_sectors", [])),
        "source_artifact": record.get("artifact_type"),
    }
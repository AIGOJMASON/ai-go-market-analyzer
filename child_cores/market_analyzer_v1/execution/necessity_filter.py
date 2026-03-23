from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


ALLOWED_SECTORS = {
    "energy",
    "agriculture",
    "fertilizer",
    "infrastructure",
    "critical_technology",
}


def _is_liquid_enough(candidate: Dict[str, Any]) -> bool:
    liquidity = str(candidate.get("liquidity", "unknown")).lower()
    return liquidity in {"high", "medium"}


def _sector_allowed(candidate: Dict[str, Any]) -> bool:
    sector = str(candidate.get("sector", "")).lower()
    return sector in ALLOWED_SECTORS


def filter_necessity_candidates(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Keep only necessity-sector, liquid candidates.
    """
    filtered: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for candidate in candidates:
        item = deepcopy(candidate)
        passes_sector = _sector_allowed(item)
        passes_liquidity = _is_liquid_enough(item)

        if passes_sector and passes_liquidity:
            item["necessity_filter_pass"] = True
            filtered.append(item)
        else:
            item["necessity_filter_pass"] = False
            item["rejection_reason"] = {
                "sector_allowed": passes_sector,
                "liquidity_allowed": passes_liquidity,
            }
            rejected.append(item)

    return {
        "artifact_type": "necessity_filtered_candidate_set",
        "core_id": "market_analyzer_v1",
        "filtered_candidates": filtered,
        "rejected_candidates": rejected,
        "allowed_sectors": sorted(ALLOWED_SECTORS),
        "filtered_count": len(filtered),
        "rejected_count": len(rejected),
    }
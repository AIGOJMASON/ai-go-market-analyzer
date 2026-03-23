from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _passes_rebound_checks(candidate: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "stabilization": bool(candidate.get("stabilization", False)),
        "reclaim": bool(candidate.get("reclaim", False)),
        "confirmation": bool(candidate.get("confirmation", False)),
        "liquidity_check": str(candidate.get("liquidity", "unknown")).lower() in {"high", "medium"},
    }


def validate_rebounds(filtered_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply required rebound checks to filtered candidates.
    """
    valid: List[Dict[str, Any]] = []
    invalid: List[Dict[str, Any]] = []

    for candidate in filtered_candidates:
        item = deepcopy(candidate)
        checks = _passes_rebound_checks(item)
        item["rebound_checks"] = checks
        item["rebound_valid"] = all(checks.values())

        if item["rebound_valid"]:
            valid.append(item)
        else:
            invalid.append(item)

    return {
        "artifact_type": "rebound_validation_record",
        "core_id": "market_analyzer_v1",
        "validated_candidates": valid,
        "rejected_candidates": invalid,
        "validated_count": len(valid),
        "rejected_count": len(invalid),
    }
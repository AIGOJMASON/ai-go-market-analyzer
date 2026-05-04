"""
RESEARCH_CORE.screening.source_credibility

Source readiness checks for research screening.
This module does not assign trust class.
It only determines whether source support is sufficient to proceed.
"""

from __future__ import annotations

from typing import Any, Dict, List


def evaluate_source_readiness(source_refs: List[Any]) -> Dict[str, Any]:
    """
    Evaluate whether a source collection is minimally ready for screening pass.
    """
    reasons: List[str] = []

    if not isinstance(source_refs, list):
        return {
            "has_minimum_source_support": False,
            "source_count": 0,
            "traceable_count": 0,
            "reasons": ["source_refs must be a list"],
        }

    if not source_refs:
        reasons.append("missing source_refs")
        return {
            "has_minimum_source_support": False,
            "source_count": 0,
            "traceable_count": 0,
            "reasons": reasons,
        }

    traceable_count = 0
    for source_ref in source_refs:
        if isinstance(source_ref, str) and source_ref.strip():
            traceable_count += 1
        elif isinstance(source_ref, dict) and str(source_ref.get("source_id", "")).strip():
            traceable_count += 1

    if traceable_count == 0:
        reasons.append("no traceable source references found")

    return {
        "has_minimum_source_support": traceable_count > 0,
        "source_count": len(source_refs),
        "traceable_count": traceable_count,
        "reasons": reasons,
    }
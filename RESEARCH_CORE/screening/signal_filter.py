"""
RESEARCH_CORE.screening.signal_filter

Structural signal checks used by the screening layer.
This module evaluates minimum usability and coherence.
"""

from __future__ import annotations

from typing import Any, Dict, List


def evaluate_signal_structure(intake_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate whether a normalized intake record is structurally usable.
    """
    reasons: List[str] = []

    title = str(intake_record.get("title", "")).strip()
    summary = str(intake_record.get("summary", "")).strip()
    scope = str(intake_record.get("scope", "")).strip()
    tags = intake_record.get("tags", [])

    is_structurally_usable = True
    needs_review = False

    if not title:
        is_structurally_usable = False
        reasons.append("missing title")

    if not summary:
        is_structurally_usable = False
        reasons.append("missing summary")

    if not scope:
        needs_review = True
        reasons.append("missing explicit scope")

    if summary and len(summary) < 20:
        needs_review = True
        reasons.append("summary too short for confident screening")

    if not isinstance(tags, list):
        needs_review = True
        reasons.append("tags should be a list")

    return {
        "is_structurally_usable": is_structurally_usable,
        "needs_review": needs_review,
        "reasons": reasons,
    }
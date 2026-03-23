"""
RESEARCH_CORE.screening.screening

Structural screening service for normalized intake records.
This module determines whether a signal may proceed to trust review.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .signal_filter import evaluate_signal_structure
from .source_credibility import evaluate_source_readiness


VALID_SCREENING_OUTCOMES = {
    "passed",
    "deferred",
    "needs_review",
    "rejected",
}


def screen_intake_record(intake_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Screen a normalized intake record and return a governed screening result.
    """
    structure_result = evaluate_signal_structure(intake_record)
    source_result = evaluate_source_readiness(intake_record.get("source_refs", []))

    outcome = "passed"
    reasons: List[str] = []

    if not structure_result["is_structurally_usable"]:
        outcome = "rejected"
        reasons.extend(structure_result["reasons"])

    if outcome == "passed" and not source_result["has_minimum_source_support"]:
        outcome = "deferred"
        reasons.extend(source_result["reasons"])

    if outcome == "passed" and structure_result["needs_review"]:
        outcome = "needs_review"
        reasons.extend(structure_result["reasons"])

    if outcome not in VALID_SCREENING_OUTCOMES:
        raise ValueError(f"invalid screening outcome produced: {outcome}")

    return {
        "screening_status": outcome,
        "structure_result": structure_result,
        "source_result": source_result,
        "reasons": reasons,
    }
"""
RESEARCH_CORE.trust.trust_model

Trust classification model for RESEARCH_CORE.
This module converts screened intake state into an explicit trust handling class.
"""

from __future__ import annotations

from typing import Any, Dict, List


VALID_TRUST_CLASSES = {
    "unverified",
    "screened",
    "corroborated",
    "restricted",
    "rejected",
}


def _count_traceable_sources(source_refs: List[Any]) -> int:
    count = 0
    for source_ref in source_refs:
        if isinstance(source_ref, str) and source_ref.strip():
            count += 1
        elif isinstance(source_ref, dict) and str(source_ref.get("source_id", "")).strip():
            count += 1
    return count


def classify_trust(*, screening_status: str, intake_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify trust based on screening state and intake characteristics.

    This is a bounded handling classifier, not a truth oracle.
    """
    source_refs = intake_record.get("source_refs", [])
    traceable_source_count = _count_traceable_sources(source_refs)
    summary = str(intake_record.get("summary", "")).strip()

    trust_class = "unverified"
    trust_rationale: List[str] = []

    if screening_status == "rejected":
        trust_class = "rejected"
        trust_rationale.append("screening rejected the input")
    elif screening_status == "deferred":
        trust_class = "unverified"
        trust_rationale.append("screening deferred the input")
    elif screening_status == "needs_review":
        trust_class = "restricted"
        trust_rationale.append("screening marked the input as needs_review")
    elif screening_status == "passed":
        if traceable_source_count >= 2 and len(summary) >= 40:
            trust_class = "corroborated"
            trust_rationale.append("multiple traceable sources present")
            trust_rationale.append("summary length supports stronger handling confidence")
        elif traceable_source_count >= 1:
            trust_class = "screened"
            trust_rationale.append("minimum source traceability present")
        else:
            trust_class = "unverified"
            trust_rationale.append("passed screening but lacks traceable source support")
    else:
        trust_class = "restricted"
        trust_rationale.append("unknown screening state")

    if trust_class not in VALID_TRUST_CLASSES:
        raise ValueError(f"invalid trust class produced: {trust_class}")

    return {
        "trust_class": trust_class,
        "trust_rationale": trust_rationale,
        "trust_inputs": {
            "screening_status": screening_status,
            "traceable_source_count": traceable_source_count,
            "summary_length": len(summary),
        },
    }
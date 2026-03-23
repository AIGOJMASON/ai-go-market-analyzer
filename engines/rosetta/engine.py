from __future__ import annotations

from typing import Any, Dict, List


def _presentation_notes(summary: str) -> List[str]:
    notes: List[str] = []

    if summary:
        notes.append("Language should remain lean, bounded, and structurally legible.")
        notes.append("Presentation refinement must not change routing or lifecycle truth.")
    else:
        notes.append("No summary text supplied for narrative shaping.")
        notes.append("PM should preserve original artifact truth and continue without stylistic expansion.")

    return notes


def run_rosetta(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rosetta is a PM-side narrative and presentation refinement engine.

    It may improve representation quality.
    It may not alter authority truth.
    """
    pm_summary = str(payload.get("pm_summary", ""))

    presentation_notes = _presentation_notes(pm_summary)

    refined_summary = pm_summary
    if pm_summary:
        refined_summary = f"PM refined summary: {pm_summary}"

    return {
        "engine_id": "rosetta",
        "refinement_type": "narrative",
        "refined_summary": refined_summary,
        "advisory_notes": presentation_notes,
        "advisory_labels": [
            "pm_narrative_refinement",
            "non_authoritative",
            "presentation_only",
        ],
    }
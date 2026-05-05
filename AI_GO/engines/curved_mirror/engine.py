from __future__ import annotations

from typing import Any, Dict, List


def _derive_reasoning_notes(summary: str, domain_focus: str | None) -> List[str]:
    notes: List[str] = []

    if domain_focus:
        notes.append(f"Domain focus recognized as '{domain_focus}'.")

    lowered = summary.lower()

    if "proposal" in lowered or "estimate" in lowered or "quote" in lowered:
        notes.append("PM should preserve contractor proposal interpretation as advisory, not authority.")
        notes.append("Child-core routing should remain grounded in PM metadata and active registry truth.")

    if "gis" in lowered or "parcel" in lowered or "zoning" in lowered or "mapping" in lowered:
        notes.append("PM should preserve GIS interpretation as advisory, not authority.")
        notes.append("Spatial-domain routing should remain grounded in PM metadata and active registry truth.")

    if not notes:
        notes.append("No strong domain-specific reasoning signature detected.")
        notes.append("PM should avoid overcommitting routing under weak interpretive weight.")

    return notes


def run_curved_mirror(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Curved Mirror is a PM-side reasoning refinement engine.

    It may improve interpretive clarity and advisory framing.
    It may not alter authority truth.
    """
    pm_summary = str(payload.get("pm_summary", ""))
    domain_focus = payload.get("domain_focus")

    reasoning_notes = _derive_reasoning_notes(pm_summary, domain_focus)

    refined_summary = pm_summary
    if reasoning_notes:
        refined_summary = f"{pm_summary} | Advisory reasoning: {reasoning_notes[0]}"

    return {
        "engine_id": "curved_mirror",
        "refinement_type": "reasoning",
        "refined_summary": refined_summary,
        "advisory_notes": reasoning_notes,
        "advisory_labels": [
            "pm_reasoning_refinement",
            "non_authoritative",
            "routing_advisory_only",
        ],
    }
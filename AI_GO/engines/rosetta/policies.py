"""
engines.rosetta.policies

Policy application helpers for the Rosetta engine.
These helpers keep narrative refinement bounded and provenance-preserving.
"""

from __future__ import annotations

from typing import Any, Dict, List


def apply_narrative_policy(gated_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply bounded narrative-refinement policy to a gated input.
    """
    summary = str(gated_input.get("summary", "")).strip()
    scope = str(gated_input.get("scope", "")).strip()

    policy_notes: List[str] = []
    allowed = True

    refined_summary = f"Narrative structure extracted from governed input: {summary}"

    if not summary:
        allowed = False
        refined_summary = ""
        policy_notes.append("missing governed summary")
    else:
        policy_notes.append("provenance-preserving narrative refinement applied")

    if not scope:
        policy_notes.append("scope missing; output should be treated with caution")

    return {
        "allowed": allowed,
        "refined_summary": refined_summary,
        "policy_notes": policy_notes,
    }
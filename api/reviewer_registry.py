from __future__ import annotations

from typing import Dict, List


# Minimal in-code registry (can move to JSON later)
REVIEWER_REGISTRY: Dict[str, Dict[str, List[str]]] = {
    "operator_primary": {
        "role": "operator",
        "permissions": ["hold", "archive_only", "escalate_to_pm"],
    },
    "pm_lead": {
        "role": "pm",
        "permissions": ["hold", "archive_only", "escalate_to_pm", "reject_invalid"],
    },
}


class ReviewerRegistryError(Exception):
    """Raised when reviewer lookup or authorization fails."""


def get_reviewer_profile(reviewer_id: str) -> Dict[str, List[str]]:
    profile = REVIEWER_REGISTRY.get(reviewer_id)
    if not profile:
        raise ReviewerRegistryError("unknown_reviewer")
    return profile


def is_decision_allowed(reviewer_id: str, decision: str) -> bool:
    profile = get_reviewer_profile(reviewer_id)
    return decision in profile.get("permissions", [])
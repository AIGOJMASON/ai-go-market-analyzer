from typing import Dict, Any, Set


APPROVED_SOURCE_TYPES: Set[str] = {
    "operator_manual",
    "newswire",
    "rss_feed",
    "watchlist_note",
    "macro_note",
    "social_observation",
}

SOURCE_TRUST_CLASSES: Dict[str, str] = {
    "operator_manual": "bounded_manual",
    "newswire": "high_structure",
    "rss_feed": "medium_structure",
    "watchlist_note": "bounded_manual",
    "macro_note": "bounded_manual",
    "social_observation": "low_structure",
}


def get_source_registry() -> Dict[str, Any]:
    return {
        "approved_source_types": sorted(APPROVED_SOURCE_TYPES),
        "source_trust_classes": dict(SOURCE_TRUST_CLASSES),
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "provenance_required": True,
    }


def validate_source_type(source_type: str) -> None:
    if source_type not in APPROVED_SOURCE_TYPES:
        approved = ", ".join(sorted(APPROVED_SOURCE_TYPES))
        raise ValueError(
            f"unsupported source_type='{source_type}'. approved values: {approved}"
        )


def resolve_trust_class(source_type: str) -> str:
    validate_source_type(source_type)
    return SOURCE_TRUST_CLASSES[source_type]

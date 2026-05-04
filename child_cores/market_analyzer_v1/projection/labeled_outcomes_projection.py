# path: /root/apps/AI_GO/child_cores/market_analyzer_v1/projection/labeled_outcomes_projection.py

from __future__ import annotations

from typing import Any, Dict, Optional

from child_cores.market_analyzer_v1.explanation.outcome_interpreter import (
    build_labeled_outcomes_panel_from_source_2_summary,
)


def build_labeled_outcomes_projection(
    payload: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Extracts labeled outcomes from source_2_summary and returns
    a clean projection panel for UI + explainer use.

    This is READ-ONLY and must not mutate:
    - recommendation_panel
    - governance_panel
    - runtime output

    It is annotation-only.
    """

    if not isinstance(payload, dict):
        return None

    # Primary source (preferred)
    source_2_summary = payload.get("source_2_summary")

    # Fallback (operator packet path)
    if not source_2_summary:
        operator_packet = payload.get("operator_packet") or {}
        source_2_summary = operator_packet.get("historical_reference")

    labeled_panel = build_labeled_outcomes_panel_from_source_2_summary(
        source_2_summary
    )

    if not labeled_panel:
        return None

    return {
        "artifact_type": "labeled_outcomes_projection",
        "status": "ok",

        "event_count": labeled_panel.get("event_count"),
        "outcome_count": labeled_panel.get("outcome_count"),

        "outcome_counts": labeled_panel.get("outcome_counts"),

        "rates": labeled_panel.get("rates"),

        "edge_class": labeled_panel.get("edge_class"),
        "historical_posture": labeled_panel.get("historical_posture"),

        # Human-facing meaning
        "operator_meaning": labeled_panel.get("operator_meaning"),
        "why_user_should_care": labeled_panel.get("why_user_should_care"),
        "confidence_note": labeled_panel.get("confidence_note"),

        # Fully composed sentence (UI ready)
        "operator_summary": labeled_panel.get("operator_summary"),

        # Hard constraint (important for governance)
        "constraints": {
            "annotation_only": True,
            "recommendation_mutation_allowed": False,
            "governance_mutation_allowed": False,
            "runtime_mutation_allowed": False,
        }
    }
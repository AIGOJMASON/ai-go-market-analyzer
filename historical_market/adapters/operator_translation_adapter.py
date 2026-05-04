from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional


class OperatorTranslationAdapter:
    """
    Read-only translation layer that turns curated retrieval results into
    simple operator-facing guidance blocks.
    """

    def build_setup_history_panel(
        self,
        *,
        setup_type: str,
        setup_summary: Mapping[str, Any],
    ) -> Dict[str, Any]:
        outcome_counts = dict(setup_summary.get("outcome_counts", {}))
        outcome_count = int(setup_summary.get("outcome_count", 0))

        follow_through_count = int(outcome_counts.get("follow_through", 0))
        failure_count = int(outcome_counts.get("failure", 0))
        stall_count = int(outcome_counts.get("stall", 0))

        follow_through_rate = round((follow_through_count / outcome_count) * 100.0, 2) if outcome_count else 0.0
        failure_rate = round((failure_count / outcome_count) * 100.0, 2) if outcome_count else 0.0

        if follow_through_rate >= 60.0:
            posture = "historically constructive"
        elif failure_rate >= 50.0:
            posture = "historically fragile"
        else:
            posture = "historically mixed"

        return {
            "panel_type": "setup_history",
            "setup_type": setup_type,
            "pattern_count": int(setup_summary.get("pattern_count", 0)),
            "outcome_count": outcome_count,
            "follow_through_rate_pct": follow_through_rate,
            "failure_rate_pct": failure_rate,
            "stall_count": stall_count,
            "historical_posture": posture,
            "operator_summary": self._build_operator_summary(
                setup_type=setup_type,
                posture=posture,
                follow_through_rate=follow_through_rate,
                failure_rate=failure_rate,
                outcome_count=outcome_count,
            ),
        }

    def build_event_package_panel(
        self,
        *,
        event_id: str,
        event_records: List[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        setup_type: Optional[str] = None
        outcome_label: Optional[str] = None

        for record in event_records:
            artifact_type = record.get("artifact_type")
            if artifact_type == "historical_setup_pattern":
                setup_type = record.get("setup_type")
            elif artifact_type == "historical_outcome_event":
                outcome_label = record.get("outcome_label")

        return {
            "panel_type": "event_package",
            "event_id": event_id,
            "record_count": len(event_records),
            "setup_type": setup_type,
            "outcome_label": outcome_label,
            "operator_summary": self._build_event_summary(
                event_id=event_id,
                setup_type=setup_type,
                outcome_label=outcome_label,
                record_count=len(event_records),
            ),
        }

    def _build_operator_summary(
        self,
        *,
        setup_type: str,
        posture: str,
        follow_through_rate: float,
        failure_rate: float,
        outcome_count: int,
    ) -> str:
        return (
            f"Historical read for {setup_type}: {posture}. "
            f"Follow-through rate {follow_through_rate:.2f}% "
            f"vs failure rate {failure_rate:.2f}% across {outcome_count} labeled outcomes."
        )

    def _build_event_summary(
        self,
        *,
        event_id: str,
        setup_type: Optional[str],
        outcome_label: Optional[str],
        record_count: int,
    ) -> str:
        return (
            f"Event {event_id} has {record_count} curated records. "
            f"Setup={setup_type or 'unknown'}, outcome={outcome_label or 'unknown'}."
        )
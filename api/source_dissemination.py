from typing import List

from AI_GO.api.source_ingress_schema import (
    SourceClusterRecord,
    SourceCandidateRecord,
    SourceSignalRecord,
    SourceInboxRecord,
)


def _resolve_suggestion_class(cluster: SourceClusterRecord, confirmation_state: str) -> str:
    if confirmation_state == "missing":
        return "dismiss"

    if cluster.suggestion_strength == "high":
        return "analyze"

    if cluster.suggestion_strength == "medium":
        return "review"

    return "monitor"


def _resolve_reason(cluster: SourceClusterRecord, suggestion_class: str) -> str:
    if suggestion_class == "analyze":
        return "Multiple aligned source records justify governed downstream analysis."
    if suggestion_class == "review":
        return "Related source records suggest a bounded candidate worth operator review."
    if suggestion_class == "monitor":
        return "Single-source signal is visible but not yet strong enough for escalation."
    return "Signal lacks sufficient confirmation for downstream analysis."


def build_candidate_records(
    signals: List[SourceSignalRecord],
    clusters: List[SourceClusterRecord],
) -> List[SourceCandidateRecord]:
    candidates: List[SourceCandidateRecord] = []

    for cluster in clusters:
        related = [
            signal
            for signal in signals
            if signal.event_theme == cluster.event_theme
            and signal.normalized_sector == cluster.normalized_sector
            and signal.normalized_symbol == cluster.normalized_symbol
        ]

        confirmation_state = "unknown"
        propagation = "neutral"

        if related:
            precedence = {"confirmed": 3, "partial": 2, "unknown": 1, "missing": 0}
            best = sorted(
                related,
                key=lambda item: precedence.get(item.normalized_confirmation, 0),
                reverse=True,
            )[0]
            confirmation_state = best.normalized_confirmation
            propagation = best.propagation

        suggestion_class = _resolve_suggestion_class(cluster, confirmation_state)

        candidates.append(
            SourceCandidateRecord(
                candidate_id=f"cand::{cluster.cluster_key}",
                cluster_key=cluster.cluster_key,
                symbol=cluster.normalized_symbol,
                sector=cluster.normalized_sector,
                event_theme=cluster.event_theme,
                source_count=cluster.source_count,
                suggestion_class=suggestion_class,
                suggestion_reason=_resolve_reason(cluster, suggestion_class),
                confirmation_state=confirmation_state,
                propagation=propagation,
            )
        )

    candidates.sort(
        key=lambda item: (
            {"analyze": 0, "review": 1, "monitor": 2, "dismiss": 3}[item.suggestion_class],
            -item.source_count,
            item.candidate_id,
        )
    )
    return candidates


def build_inbox_record(
    signals: List[SourceSignalRecord],
    candidates: List[SourceCandidateRecord],
) -> SourceInboxRecord:
    summary = {
        "signal_count": len(signals),
        "candidate_count": len(candidates),
        "analyze_count": sum(1 for item in candidates if item.suggestion_class == "analyze"),
        "review_count": sum(1 for item in candidates if item.suggestion_class == "review"),
        "monitor_count": sum(1 for item in candidates if item.suggestion_class == "monitor"),
        "dismiss_count": sum(1 for item in candidates if item.suggestion_class == "dismiss"),
    }

    return SourceInboxRecord(
        incoming_signals=signals,
        candidate_cases=candidates,
        summary=summary,
    )
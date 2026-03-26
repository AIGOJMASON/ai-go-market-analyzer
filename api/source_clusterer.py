from collections import defaultdict
from typing import Dict, List

from AI_GO.api.source_ingress_schema import (
    SourceSignalRecord,
    SourceClusterMember,
    SourceClusterRecord,
)


def build_cluster_key(signal: SourceSignalRecord) -> str:
    symbol = signal.normalized_symbol or "NO_SYMBOL"
    sector = signal.normalized_sector
    theme = signal.event_theme
    return f"{theme}::{sector}::{symbol}"


def cluster_signals(signals: List[SourceSignalRecord]) -> List[SourceClusterRecord]:
    grouped: Dict[str, List[SourceSignalRecord]] = defaultdict(list)
    for signal in signals:
        grouped[build_cluster_key(signal)].append(signal)

    clusters: List[SourceClusterRecord] = []
    for cluster_key, members in grouped.items():
        first = members[0]
        source_count = len(members)

        if source_count >= 3:
            suggestion_strength = "high"
        elif source_count == 2:
            suggestion_strength = "medium"
        else:
            suggestion_strength = "low"

        cluster_members = [
            SourceClusterMember(
                source_item_id=item.source_item_id,
                headline=item.headline,
                source_type=item.source_type,
                severity=item.severity,
                event_theme=item.event_theme,
                normalized_symbol=item.normalized_symbol,
                normalized_sector=item.normalized_sector,
            )
            for item in members
        ]

        clusters.append(
            SourceClusterRecord(
                cluster_key=cluster_key,
                event_theme=first.event_theme,
                normalized_symbol=first.normalized_symbol,
                normalized_sector=first.normalized_sector,
                source_count=source_count,
                suggestion_strength=suggestion_strength,
                members=cluster_members,
            )
        )

    clusters.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}[item.suggestion_strength],
            -item.source_count,
            item.cluster_key,
        )
    )
    return clusters
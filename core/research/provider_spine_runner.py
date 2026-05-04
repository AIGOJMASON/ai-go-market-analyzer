from __future__ import annotations

from typing import Any

from AI_GO.core.research.ingress.alpha_research_ingress import (
    build_alpha_quote_research_packet,
)
from AI_GO.core.research.ingress.marketaux_research_ingress import (
    build_marketaux_event_research_packets,
)
from AI_GO.core.root_intelligence_spine import run_root_intelligence_spine


def run_alpha_quote_through_root_spine(
    *,
    symbol: str,
    child_core_targets: list[str],
    sector: str = "unknown",
    confirmation: str = "partial",
    curation_approved: bool = False,
    intake_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    research_packet = build_alpha_quote_research_packet(
        symbol=symbol,
        child_core_targets=child_core_targets,
        sector=sector,
        confirmation=confirmation,
        intake_context=intake_context or {},
    )

    return run_root_intelligence_spine(
        research_packet=research_packet,
        curation_approved=curation_approved,
    )


def run_marketaux_news_through_root_spine(
    *,
    symbols: list[str] | None = None,
    published_after: str | None = None,
    child_core_targets: list[str] | None = None,
    sector: str = "unknown",
    confirmation: str = "partial",
    limit: int = 10,
    curation_approved: bool = False,
    intake_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    research_packets = build_marketaux_event_research_packets(
        symbols=symbols,
        published_after=published_after,
        child_core_targets=child_core_targets or [],
        sector=sector,
        confirmation=confirmation,
        limit=limit,
        intake_context=intake_context or {},
    )

    return {
        "status": "ok",
        "provider": "marketaux",
        "packet_count": len(research_packets),
        "spine_results": [
            run_root_intelligence_spine(
                research_packet=packet,
                curation_approved=curation_approved,
            )
            for packet in research_packets
        ],
    }
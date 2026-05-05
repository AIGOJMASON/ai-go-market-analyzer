from __future__ import annotations

from typing import Any

from AI_GO.core.research.ingress.provider_research_ingress import (
    build_research_packet_from_provider_result,
)
from AI_GO.core.research.providers.marketaux_event_provider import fetch_marketaux_news


def build_marketaux_event_research_packets(
    *,
    symbols: list[str] | None = None,
    published_after: str | None = None,
    child_core_targets: list[str] | None = None,
    sector: str = "unknown",
    confirmation: str = "partial",
    limit: int = 10,
    intake_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    targets = child_core_targets or []
    result = fetch_marketaux_news(
        symbols=symbols,
        published_after=published_after,
        limit=limit,
    )

    data = result.payload.get("data", [])
    packets: list[dict[str, Any]] = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            continue

        title = str(item.get("title") or item.get("headline") or "").strip()
        summary = str(item.get("description") or item.get("snippet") or title).strip()

        entities = item.get("entities")
        symbol = ""
        if isinstance(entities, list):
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                symbol = str(entity.get("symbol") or "").strip().upper()
                if symbol:
                    break

        if not title:
            continue

        packets.append(
            build_research_packet_from_provider_result(
                result=result,
                title=title,
                summary=summary,
                signal_type="market_event_news",
                child_core_targets=targets,
                symbol=symbol,
                symbols=symbols or [],
                sector=sector,
                confirmation=confirmation,
                source_material=[
                    {
                        "type": "provider_news_item",
                        "provider": "marketaux",
                        "index": index,
                        "title": title,
                        "symbol": symbol,
                        "published_at": item.get("published_at"),
                    }
                ],
                source_refs=[
                    item.get("url")
                    or item.get("source")
                    or f"marketaux:item:{index}"
                ],
                intake_context=intake_context or {},
            )
        )

    return packets
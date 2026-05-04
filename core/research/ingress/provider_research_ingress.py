from __future__ import annotations

from typing import Any

from AI_GO.core.research.live_research_gateway import build_live_research_packet
from AI_GO.core.research.providers.provider_result_schema import ProviderFetchResult


def build_research_packet_from_provider_result(
    *,
    result: ProviderFetchResult,
    title: str,
    summary: str,
    signal_type: str,
    child_core_targets: list[str],
    symbol: str = "",
    symbols: list[str] | None = None,
    sector: str = "unknown",
    confirmation: str = "partial",
    source_material: list[dict[str, Any]] | None = None,
    source_refs: list[Any] | None = None,
    intake_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ctx = dict(result.request_context)

    return build_live_research_packet(
        {
            "provider": result.provider,
            "provider_kind": result.provider_kind,
            "source_type": ctx.get("source_type", "verified_api"),
            "signal_type": signal_type,
            "title": title,
            "summary": summary,
            "symbol": symbol or ctx.get("symbol", ""),
            "symbols": symbols or ctx.get("symbols", []),
            "price": ctx.get("price"),
            "price_change_pct": ctx.get("price_change_pct"),
            "sector": sector,
            "confirmation": confirmation,
            "observed_at": result.fetched_at,
            "provider_payload": result.payload,
            "source_material": source_material or [],
            "source_refs": source_refs or [],
            "intake_context": intake_context or {},
            "child_core_targets": child_core_targets,
        }
    )
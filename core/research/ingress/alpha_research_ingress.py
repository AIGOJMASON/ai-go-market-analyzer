from __future__ import annotations

from typing import Any

from AI_GO.core.research.ingress.provider_research_ingress import (
    build_research_packet_from_provider_result,
)
from AI_GO.core.research.providers.alpha_vantage_quote_provider import (
    fetch_alpha_vantage_quote,
)


def build_alpha_quote_research_packet(
    *,
    symbol: str,
    child_core_targets: list[str],
    sector: str = "unknown",
    confirmation: str = "partial",
    intake_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = fetch_alpha_vantage_quote(symbol=symbol)
    ctx = dict(result.request_context)

    change = float(ctx.get("price_change_pct", 0.0) or 0.0)
    direction = "up" if change >= 0 else "down"

    return build_research_packet_from_provider_result(
        result=result,
        title=f"Alpha Vantage quote signal for {ctx.get('symbol', symbol)}",
        summary=(
            f"Verified quote provider reports {ctx.get('symbol', symbol)} "
            f"{direction} {abs(change):.2f}% with current price {ctx.get('price')}."
        ),
        signal_type="market_quote",
        child_core_targets=child_core_targets,
        symbol=str(ctx.get("symbol", symbol)).upper(),
        sector=sector,
        confirmation=confirmation,
        source_material=[
            {
                "type": "provider_quote",
                "provider": "alpha_vantage",
                "symbol": str(ctx.get("symbol", symbol)).upper(),
                "price": ctx.get("price"),
                "price_change_pct": change,
            }
        ],
        source_refs=["alpha_vantage:GLOBAL_QUOTE"],
        intake_context=intake_context or {},
    )
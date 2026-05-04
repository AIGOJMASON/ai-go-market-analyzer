from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from AI_GO.core.research.provider_spine_runner import (
    run_marketaux_news_through_root_spine,
)


class MarketauxEventIngressRunnerError(RuntimeError):
    pass


@dataclass(frozen=True)
class EventIngressRunResult:
    provider: str
    requested_symbols: list[str]
    published_after: str | None
    root_spine_response: dict[str, Any]
    migration_status: str = "provider_authority_moved_to_RESEARCH_CORE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "requested_symbols": self.requested_symbols,
            "published_after": self.published_after,
            "migration_status": self.migration_status,
            "root_spine_response": self.root_spine_response,
            "authority": {
                "provider_clients_inside_child_core_allowed": False,
                "direct_post_to_market_analyzer_live_allowed": False,
                "post_to_live_ignored": True,
                "research_core_required": True,
                "engines_required_before_child_core": True,
                "raw_provider_payload_to_child_core_allowed": False,
            },
        }


def _normalize_symbols(symbols: list[str] | None) -> list[str]:
    normalized: list[str] = []

    for symbol in symbols or []:
        clean = str(symbol or "").strip().upper()
        if clean:
            normalized.append(clean)

    return normalized


def run_marketaux_event_ingress(
    symbols: list[str] | None = None,
    published_after: str | None = None,
    post_to_live: bool = False,
    *,
    child_core_targets: list[str] | None = None,
    sector: str = "unknown",
    confirmation: str = "partial",
    limit: int = 10,
    curation_approved: bool = False,
) -> dict[str, Any]:
    """
    Compatibility wrapper.

    Provider authority no longer lives in market_analyzer_v1.

    Old behavior:
        Marketaux provider -> child-core normalizer
        -> optional POST /market-analyzer/run/live

    New lawful behavior:
        Marketaux provider -> RESEARCH_CORE -> engines curated handoff
        -> optional child-core read only after curation

    post_to_live is intentionally ignored because direct child-core live posting
    is no longer lawful.
    """
    clean_symbols = _normalize_symbols(symbols)
    targets = child_core_targets or ["market_analyzer_v1"]

    root_spine_response = run_marketaux_news_through_root_spine(
        symbols=clean_symbols or None,
        published_after=published_after,
        child_core_targets=targets,
        sector=sector,
        confirmation=confirmation,
        limit=limit,
        curation_approved=curation_approved,
        intake_context={
            "compatibility_wrapper": (
                "AI_GO.child_cores.market_analyzer_v1.data_sources."
                "marketaux_event_ingress_runner"
            ),
            "migration_note": "marketaux_provider_authority_moved_to_RESEARCH_CORE",
            "direct_live_post_disabled": True,
            "post_to_live_requested": bool(post_to_live),
            "post_to_live_ignored": True,
        },
    )

    return EventIngressRunResult(
        provider="marketaux",
        requested_symbols=clean_symbols,
        published_after=published_after,
        root_spine_response=root_spine_response,
    ).to_dict()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Fetch Marketaux news through RESEARCH_CORE and engines. "
            "This wrapper no longer posts directly to Market Analyzer live route."
        )
    )
    parser.add_argument(
        "--symbols",
        default="",
        help="Comma-separated symbols such as XLE,XLU",
    )
    parser.add_argument(
        "--published-after",
        default="",
        help="Optional provider query lower bound timestamp",
    )
    parser.add_argument(
        "--post-to-live",
        action="store_true",
        help="Deprecated. Ignored. Direct live posting is no longer lawful.",
    )
    parser.add_argument(
        "--targets",
        default="market_analyzer_v1",
        help="Comma-separated child-core targets. Default: market_analyzer_v1",
    )
    parser.add_argument("--sector", default="unknown")
    parser.add_argument("--confirmation", default="partial")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--curation-approved",
        action="store_true",
        help="Allow curated external-memory path if downstream policy accepts it.",
    )

    args = parser.parse_args()

    symbol_list = [
        part.strip().upper()
        for part in args.symbols.split(",")
        if part.strip()
    ]
    target_list = [
        item.strip()
        for item in args.targets.split(",")
        if item.strip()
    ]

    result = run_marketaux_event_ingress(
        symbols=symbol_list or None,
        published_after=args.published_after.strip() or None,
        post_to_live=bool(args.post_to_live),
        child_core_targets=target_list or ["market_analyzer_v1"],
        sector=args.sector,
        confirmation=args.confirmation,
        limit=args.limit,
        curation_approved=bool(args.curation_approved),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
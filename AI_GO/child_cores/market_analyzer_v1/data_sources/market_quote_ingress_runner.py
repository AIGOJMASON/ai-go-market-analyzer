from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from AI_GO.core.research.provider_spine_runner import (
    run_alpha_quote_through_root_spine,
)


class MarketQuoteIngressRunnerError(RuntimeError):
    pass


@dataclass(frozen=True)
class QuoteIngressRunResult:
    provider: str
    root_spine_response: dict[str, Any]
    migration_status: str = "provider_authority_moved_to_RESEARCH_CORE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "migration_status": self.migration_status,
            "root_spine_response": self.root_spine_response,
            "authority": {
                "provider_clients_inside_child_core_allowed": False,
                "direct_post_to_market_analyzer_live_allowed": False,
                "research_core_required": True,
                "engines_required_before_child_core": True,
                "raw_provider_payload_to_child_core_allowed": False,
            },
        }


def run_market_quote_ingress(
    symbol: str,
    *,
    child_core_targets: list[str] | None = None,
    sector: str = "unknown",
    confirmation: str = "partial",
    curation_approved: bool = False,
) -> dict[str, Any]:
    """
    Compatibility wrapper.

    Provider authority no longer lives in market_analyzer_v1.

    Old behavior:
        Alpha provider -> child-core normalizer -> POST /market-analyzer/run/live

    New lawful behavior:
        Alpha provider -> RESEARCH_CORE -> engines curated handoff
        -> optional child-core read only after curation

    This function intentionally does not post directly to /market-analyzer/run/live.
    """
    clean_symbol = str(symbol or "").strip().upper()
    if not clean_symbol:
        raise MarketQuoteIngressRunnerError("symbol_required")

    targets = child_core_targets or ["market_analyzer_v1"]

    root_spine_response = run_alpha_quote_through_root_spine(
        symbol=clean_symbol,
        child_core_targets=targets,
        sector=sector,
        confirmation=confirmation,
        curation_approved=curation_approved,
        intake_context={
            "compatibility_wrapper": (
                "AI_GO.child_cores.market_analyzer_v1.data_sources."
                "market_quote_ingress_runner"
            ),
            "migration_note": "alpha_provider_authority_moved_to_RESEARCH_CORE",
            "direct_live_post_disabled": True,
        },
    )

    return QuoteIngressRunResult(
        provider="alpha_vantage",
        root_spine_response=root_spine_response,
    ).to_dict()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Fetch a quote through RESEARCH_CORE and engines. "
            "This wrapper no longer posts directly to Market Analyzer live route."
        )
    )
    parser.add_argument("--symbol", required=True, help="Allowed symbol such as XLE")
    parser.add_argument(
        "--targets",
        default="market_analyzer_v1",
        help="Comma-separated child-core targets. Default: market_analyzer_v1",
    )
    parser.add_argument("--sector", default="unknown")
    parser.add_argument("--confirmation", default="partial")
    parser.add_argument(
        "--curation-approved",
        action="store_true",
        help="Allow curated external-memory path if downstream policy accepts it.",
    )

    args = parser.parse_args()

    target_list = [
        item.strip()
        for item in args.targets.split(",")
        if item.strip()
    ]

    result = run_market_quote_ingress(
        symbol=args.symbol,
        child_core_targets=target_list or ["market_analyzer_v1"],
        sector=args.sector,
        confirmation=args.confirmation,
        curation_approved=bool(args.curation_approved),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
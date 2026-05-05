from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

try:
    from historical_market.storage.curated_store import CuratedStore
except ImportError:
    from AI_GO.historical_market.storage.curated_store import CuratedStore  # type: ignore

try:
    from child_cores.market_analyzer_v1.data_sources.marketaux_event_client import MarketauxEventClient
    from child_cores.market_analyzer_v1.data_sources.marketaux_event_normalizer import MarketauxEventNormalizer
    from child_cores.market_analyzer_v1.data_sources.marketaux_event_policy import MarketauxEventPolicy
except ImportError:
    from AI_GO.child_cores.market_analyzer_v1.data_sources.marketaux_event_client import MarketauxEventClient  # type: ignore
    from AI_GO.child_cores.market_analyzer_v1.data_sources.marketaux_event_normalizer import MarketauxEventNormalizer  # type: ignore
    from AI_GO.child_cores.market_analyzer_v1.data_sources.marketaux_event_policy import MarketauxEventPolicy  # type: ignore


class MarketauxHistoricalIntakeRunnerError(RuntimeError):
    """Raised when Marketaux historical intake cannot be completed lawfully."""


@dataclass(frozen=True)
class HistoricalIntakeWriteRecord:
    status: str
    event_id: str
    artifact_path: str
    index_path: str
    receipt_path: str
    symbol: str
    sector: str
    signal_seed: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "event_id": self.event_id,
            "artifact_path": self.artifact_path,
            "index_path": self.index_path,
            "receipt_path": self.receipt_path,
            "symbol": self.symbol,
            "sector": self.sector,
            "signal_seed": self.signal_seed,
        }


@dataclass(frozen=True)
class MarketauxHistoricalIntakeRunResult:
    status: str
    provider: str
    requested_symbols: List[str]
    published_after: Optional[str]
    fetched_count: int
    accepted_for_write_count: int
    skipped_count: int
    written_count: int
    writes: List[Dict[str, Any]]
    skipped: List[Dict[str, Any]]
    runner_receipt: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "provider": self.provider,
            "requested_symbols": list(self.requested_symbols),
            "published_after": self.published_after,
            "fetched_count": self.fetched_count,
            "accepted_for_write_count": self.accepted_for_write_count,
            "skipped_count": self.skipped_count,
            "written_count": self.written_count,
            "writes": list(self.writes),
            "skipped": list(self.skipped),
            "runner_receipt": dict(self.runner_receipt),
        }


class MarketauxHistoricalIntakeRunner:
    """
    Marketaux historical event -> canonical event -> curated historical intake event.

    Responsibilities:
    - fetch Marketaux event history
    - normalize provider payload into canonical event ingress requests
    - map canonical event requests into historical_intake_event records
    - write those records into CuratedStore

    Non-responsibilities:
    - posting into /market-analyzer/run/live
    - PM routing
    - setup detection
    - outcome labeling
    - relationship derivation
    - recommendation mutation
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        policy: Optional[MarketauxEventPolicy] = None,
        client: Optional[MarketauxEventClient] = None,
        normalizer: Optional[MarketauxEventNormalizer] = None,
        curated_store: Optional[CuratedStore] = None,
        skip_symbol_less_events: bool = True,
        default_asset_class: str = "etf",
        default_timeframe: str = "event",
    ) -> None:
        self.policy = policy or MarketauxEventPolicy()
        effective_api_key = (api_key or os.getenv("MARKETAUX_API_KEY", "")).strip()
        if client is None:
            if not effective_api_key:
                raise MarketauxHistoricalIntakeRunnerError("missing_environment_variable:MARKETAUX_API_KEY")
            client = MarketauxEventClient(api_key=effective_api_key, policy=self.policy)

        self.client = client
        self.normalizer = normalizer or MarketauxEventNormalizer(policy=self.policy)
        self.curated_store = curated_store or CuratedStore()
        self.skip_symbol_less_events = bool(skip_symbol_less_events)
        self.default_asset_class = str(default_asset_class).strip().lower() or "etf"
        self.default_timeframe = str(default_timeframe).strip().lower() or "event"

    def run(
        self,
        *,
        symbols: Optional[List[str]] = None,
        published_after: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> MarketauxHistoricalIntakeRunResult:
        raw_news = self.client.fetch_news(
            symbols=symbols,
            published_after=published_after,
            limit=limit,
        )
        canonical_batch = self.normalizer.normalize(raw_news)

        writes: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []
        accepted_for_write_count = 0

        for request in canonical_batch.requests:
            intake_record_or_none, skip_reason = self._canonical_request_to_intake_event(request.to_dict())
            if intake_record_or_none is None:
                skipped.append(
                    {
                        "request_id": request.request_id,
                        "symbol": request.symbol,
                        "sector": request.sector,
                        "reason": skip_reason or "skipped",
                    }
                )
                continue

            accepted_for_write_count += 1
            write_result = self.curated_store.write_intake_event(intake_record_or_none)
            writes.append(
                HistoricalIntakeWriteRecord(
                    status=write_result.status,
                    event_id=intake_record_or_none["event_id"],
                    artifact_path=write_result.artifact_path,
                    index_path=write_result.index_path,
                    receipt_path=write_result.receipt_path,
                    symbol=intake_record_or_none["symbol"],
                    sector=str(intake_record_or_none["normalized_signal"].get("sector", "unknown")),
                    signal_seed=intake_record_or_none["signal_seed"],
                ).to_dict()
            )

        runner_receipt = {
            "receipt_type": "historical_marketaux_intake_runner_receipt",
            "status": "ok",
            "provider": raw_news.provider,
            "requested_symbols": list(raw_news.requested_symbols),
            "published_after": raw_news.published_after,
            "fetched_count": len(raw_news.payload.get("data", [])) if isinstance(raw_news.payload.get("data"), list) else 0,
            "normalized_count": canonical_batch.request_count,
            "accepted_for_write_count": accepted_for_write_count,
            "skipped_count": len(skipped),
            "written_count": len(writes),
            "skipped": skipped,
            "written_event_ids": [item["event_id"] for item in writes],
        }

        return MarketauxHistoricalIntakeRunResult(
            status="ok",
            provider=raw_news.provider,
            requested_symbols=list(raw_news.requested_symbols),
            published_after=raw_news.published_after,
            fetched_count=runner_receipt["fetched_count"],
            accepted_for_write_count=accepted_for_write_count,
            skipped_count=len(skipped),
            written_count=len(writes),
            writes=writes,
            skipped=skipped,
            runner_receipt=runner_receipt,
        )

    def _canonical_request_to_intake_event(
        self,
        request: Mapping[str, Any],
    ) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        request_id = str(request.get("request_id", "")).strip()
        if not request_id:
            return None, "missing_request_id"

        symbol = str(request.get("symbol") or "").strip().upper()
        if not symbol and self.skip_symbol_less_events:
            return None, "symbol_missing"

        observed_at = str(request.get("observed_at") or "").strip()
        published_at = str(request.get("published_at") or "").strip()

        # Critical fix:
        # Historical intake must anchor to the article/event publish time first,
        # not the runner observation time. Otherwise old articles get stored as
        # if they happened "now", and outcome derivation will fail because no
        # future bars exist beyond the current edge of time.
        intake_timestamp = published_at or observed_at
        if not intake_timestamp:
            return None, "timestamp_missing"

        sector = str(request.get("sector") or "unknown").strip().lower() or "unknown"
        headline = str(request.get("headline") or "").strip()
        event_theme_candidate = str(request.get("event_theme_candidate") or "").strip().lower()
        confirmation = str(request.get("confirmation") or "").strip().lower()
        signal_seed = event_theme_candidate or confirmation or "unknown"

        normalized_signal = {
            "source": request.get("source"),
            "source_type": request.get("source_type"),
            "symbol": symbol,
            "sector": sector,
            "event_theme_candidate": event_theme_candidate,
            "confirmation": confirmation,
            "observed_at": observed_at or None,
            "published_at": published_at or None,
            "provider_metadata": dict(request.get("provider_metadata") or {}),
        }

        return {
            "event_id": request_id,
            "intake_timestamp": intake_timestamp,
            "symbol": symbol or "UNKNOWN",
            "asset_class": self.default_asset_class,
            "timeframe": self.default_timeframe,
            "signal_seed": signal_seed,
            "source_ref": str(request.get("source_url") or "").strip(),
            "headline": headline,
            "raw_signal": dict(request),
            "normalized_signal": normalized_signal,
        }, None


def run_marketaux_historical_intake(
    *,
    symbols: Optional[List[str]] = None,
    published_after: Optional[str] = None,
    limit: Optional[int] = None,
    skip_symbol_less_events: bool = True,
) -> Dict[str, Any]:
    runner = MarketauxHistoricalIntakeRunner(skip_symbol_less_events=skip_symbol_less_events)
    return runner.run(
        symbols=symbols,
        published_after=published_after,
        limit=limit,
    ).to_dict()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch Marketaux historical events and write them into curated historical intake storage."
    )
    parser.add_argument(
        "--symbols",
        default="",
        help="Comma-separated allowed symbols such as XLE,XLP",
    )
    parser.add_argument(
        "--published-after",
        default="",
        help="Optional provider lower-bound timestamp",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional provider request limit override",
    )
    parser.add_argument(
        "--allow-symbol-less-events",
        action="store_true",
        help="Store events even when no allowed symbol could be extracted.",
    )
    args = parser.parse_args()

    symbol_list = [part.strip().upper() for part in args.symbols.split(",") if part.strip()]
    published_after = args.published_after.strip() or None

    result = run_marketaux_historical_intake(
        symbols=symbol_list or None,
        published_after=published_after,
        limit=args.limit,
        skip_symbol_less_events=not args.allow_symbol_less_events,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from historical_market.loaders.source_client_alpha_vantage import AlphaVantageClient
from historical_market.normalization.bar_normalizer import BarNormalizer
from historical_market.storage.raw_store import RawBarWriteResult, RawStore


UTC = timezone.utc


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class HistoricalBackfillRunResult:
    status: str
    source: str
    symbol: str
    asset_class: str
    timeframe: str
    fetched_at: str
    normalized_record_count: int
    raw_write_partition_count: int
    raw_write_results: list[dict[str, Any]]
    runner_receipt: dict[str, Any]


class HistoricalBackfillRunner:
    """
    Bounded historical loader:
    - fetches from provider
    - normalizes provider payload
    - appends normalized bars into raw storage
    - returns a runner-level summary

    It does not:
    - derive setups
    - derive outcomes
    - derive relationships
    - write curated records
    """

    def __init__(
        self,
        *,
        alpha_vantage_client: Optional[AlphaVantageClient] = None,
        normalizer: Optional[BarNormalizer] = None,
        raw_store: Optional[RawStore] = None,
    ) -> None:
        self.alpha_vantage_client = alpha_vantage_client or AlphaVantageClient()
        self.normalizer = normalizer or BarNormalizer()
        self.raw_store = raw_store or RawStore()

    def run_alpha_vantage_daily_backfill(
        self,
        *,
        symbol: str,
        asset_class: str,
        outputsize: str = "full",
        receipt_id: Optional[str] = None,
        currency: str = "",
        ingest_metadata: Optional[Mapping[str, Any]] = None,
    ) -> HistoricalBackfillRunResult:
        fetch_result = self.alpha_vantage_client.fetch_daily_series(
            symbol=symbol,
            outputsize=outputsize,
            datatype="json",
        )

        batch = self.normalizer.normalize_alpha_vantage_daily_series(
            symbol=fetch_result.symbol,
            asset_class=asset_class,
            time_series=fetch_result.time_series,
            fetched_at=fetch_result.fetched_at,
            adjusted=False,
            provider_symbol=fetch_result.symbol,
            currency=currency,
            ingest_metadata={
                "provider": "alpha_vantage",
                "function": fetch_result.requested_function,
                "outputsize": fetch_result.outputsize,
                **dict(ingest_metadata or {}),
            },
        )

        effective_receipt_id = receipt_id or self._build_receipt_id(
            source="alpha_vantage",
            symbol=fetch_result.symbol,
            fetched_at=fetch_result.fetched_at,
        )

        raw_results = self.raw_store.append_normalized_bars(
            batch.bars,
            receipt_id=effective_receipt_id,
            source="alpha_vantage",
            fetch_started_at=None,
            fetch_completed_at=fetch_result.fetched_at,
            batch_metadata={
                "runner": "historical_backfill_runner",
                "symbol": fetch_result.symbol,
                "asset_class": asset_class,
                "record_count": batch.record_count,
                "meta_data": fetch_result.meta_data,
            },
        )

        return HistoricalBackfillRunResult(
            status="ok",
            source="alpha_vantage",
            symbol=fetch_result.symbol,
            asset_class=asset_class,
            timeframe=batch.timeframe,
            fetched_at=fetch_result.fetched_at,
            normalized_record_count=batch.record_count,
            raw_write_partition_count=len(raw_results),
            raw_write_results=[self._raw_write_result_to_dict(item) for item in raw_results],
            runner_receipt={
                "receipt_type": "historical_market_backfill_runner_receipt",
                "status": "ok",
                "source": "alpha_vantage",
                "symbol": fetch_result.symbol,
                "asset_class": asset_class,
                "timeframe": batch.timeframe,
                "fetched_at": fetch_result.fetched_at,
                "normalized_record_count": batch.record_count,
                "raw_write_partition_count": len(raw_results),
                "raw_receipt_paths": [item.receipt_path for item in raw_results],
                "created_at": _utc_now_iso(),
            },
        )

    def _build_receipt_id(self, *, source: str, symbol: str, fetched_at: str) -> str:
        cleaned = fetched_at.replace(":", "").replace("-", "").replace("+00:00", "Z")
        return f"{source}-{symbol}-{cleaned}"

    def _raw_write_result_to_dict(self, result: RawBarWriteResult) -> Dict[str, Any]:
        return {
            "status": result.status,
            "record_count": result.record_count,
            "output_path": result.output_path,
            "receipt_path": result.receipt_path,
            "written_at": result.written_at,
        }
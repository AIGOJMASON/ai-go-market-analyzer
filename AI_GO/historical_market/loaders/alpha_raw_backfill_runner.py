from __future__ import annotations

import json
import argparse

from historical_market.loaders.historical_backfill_runner import HistoricalBackfillRunner


def run_alpha_raw_backfill(
    *,
    symbol: str,
    asset_class: str,
    outputsize: str = "full",
    currency: str = "",
) -> dict:
    runner = HistoricalBackfillRunner()
    result = runner.run_alpha_vantage_daily_backfill(
        symbol=symbol,
        asset_class=asset_class,
        outputsize=outputsize,
        currency=currency,
    )
    return {
        "status": result.status,
        "source": result.source,
        "symbol": result.symbol,
        "asset_class": result.asset_class,
        "timeframe": result.timeframe,
        "fetched_at": result.fetched_at,
        "normalized_record_count": result.normalized_record_count,
        "raw_write_partition_count": result.raw_write_partition_count,
        "raw_write_results": result.raw_write_results,
        "runner_receipt": result.runner_receipt,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill raw daily bars from Alpha Vantage into historical_market/raw/bars."
    )
    parser.add_argument("--symbol", required=True, help="Allowed symbol such as XLP or XLE")
    parser.add_argument("--asset-class", required=True, help="Asset class such as etf")
    parser.add_argument("--outputsize", default="full", choices=["compact", "full"])
    parser.add_argument("--currency", default="")
    args = parser.parse_args()

    result = run_alpha_raw_backfill(
        symbol=args.symbol,
        asset_class=args.asset_class,
        outputsize=args.outputsize,
        currency=args.currency,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
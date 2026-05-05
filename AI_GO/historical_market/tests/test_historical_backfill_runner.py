from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from historical_market.loaders.historical_backfill_runner import HistoricalBackfillRunner
from historical_market.normalization.bar_normalizer import BarNormalizer
from historical_market.storage.db_paths import HistoricalMarketPaths
from historical_market.storage.raw_store import RawStore


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


class FakeAlphaVantageClient:
    def fetch_daily_series(self, *, symbol: str, outputsize: str = "full", datatype: str = "json"):
        return type(
            "FakeFetchResult",
            (),
            {
                "status": "ok",
                "source": "alpha_vantage",
                "symbol": symbol.upper(),
                "requested_function": "TIME_SERIES_DAILY",
                "outputsize": outputsize,
                "fetched_at": "2026-04-06T13:00:00+00:00",
                "meta_data": {
                    "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                    "2. Symbol": symbol.upper(),
                },
                "time_series": {
                    "2026-04-01": {
                        "1. open": "93.10",
                        "2. high": "94.25",
                        "3. low": "92.80",
                        "4. close": "94.00",
                        "5. volume": "12345678",
                    },
                    "2026-04-02": {
                        "1. open": "94.00",
                        "2. high": "94.90",
                        "3. low": "93.60",
                        "4. close": "94.77",
                        "5. volume": "11335577",
                    },
                },
                "raw_response": {},
            },
        )()


class TestHistoricalBackfillRunner(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_hist_backfill_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()

        self.runner = HistoricalBackfillRunner(
            alpha_vantage_client=FakeAlphaVantageClient(),
            normalizer=BarNormalizer(),
            raw_store=RawStore(paths=self.paths),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_run_alpha_vantage_daily_backfill(self) -> None:
        result = self.runner.run_alpha_vantage_daily_backfill(
            symbol="XLE",
            asset_class="etf",
            outputsize="full",
            receipt_id="backfill-smoke-001",
            ingest_metadata={"mode": "test"},
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.source, "alpha_vantage")
        self.assertEqual(result.symbol, "XLE")
        self.assertEqual(result.asset_class, "etf")
        self.assertEqual(result.timeframe, "1d")
        self.assertEqual(result.normalized_record_count, 2)
        self.assertEqual(result.raw_write_partition_count, 1)

        self.assertEqual(result.runner_receipt["receipt_type"], "historical_market_backfill_runner_receipt")
        self.assertEqual(result.runner_receipt["symbol"], "XLE")
        self.assertEqual(len(result.runner_receipt["raw_receipt_paths"]), 1)

        month_file = self.paths.raw_bar_month_file(
            asset_class="etf",
            symbol="XLE",
            year="2026",
            month="04",
        )
        self.assertTrue(month_file.exists())

        rows = _read_jsonl(month_file)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["symbol"], "XLE")
        self.assertEqual(rows[0]["timeframe"], "1d")
        self.assertEqual(rows[1]["close"], 94.77)

        raw_receipt_path = Path(result.raw_write_results[0]["receipt_path"])
        self.assertTrue(raw_receipt_path.exists())

        raw_receipt = _read_json(raw_receipt_path)
        self.assertEqual(raw_receipt["receipt_type"], "historical_market_raw_write_receipt")
        self.assertEqual(raw_receipt["symbol"], "XLE")
        self.assertEqual(raw_receipt["asset_class"], "etf")
        self.assertEqual(raw_receipt["record_count"], 2)


if __name__ == "__main__":
    unittest.main()
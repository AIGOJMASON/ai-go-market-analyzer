from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

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


class TestRawStoreSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_hist_market_raw_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()
        self.store = RawStore(paths=self.paths)

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_append_normalized_bars_single_partition(self) -> None:
        bars = [
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 93.10,
                "high": 94.25,
                "low": 92.80,
                "close": 94.00,
                "volume": 12345678,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            },
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 94.00,
                "high": 94.90,
                "low": 93.60,
                "close": 94.77,
                "volume": 11335577,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            },
        ]

        results = self.store.append_normalized_bars(
            bars,
            receipt_id="raw-batch-001",
            source="alpha_vantage",
            fetch_started_at="2026-04-06T12:59:00+00:00",
            fetch_completed_at="2026-04-06T13:00:00+00:00",
            batch_metadata={"mode": "smoke_test"},
        )

        self.assertEqual(len(results), 1)

        result = results[0]
        self.assertEqual(result.status, "written")
        self.assertEqual(result.record_count, 2)

        output_path = Path(result.output_path)
        receipt_path = Path(result.receipt_path)

        self.assertTrue(output_path.exists())
        self.assertTrue(receipt_path.exists())

        written_rows = _read_jsonl(output_path)
        self.assertEqual(len(written_rows), 2)
        self.assertEqual(written_rows[0]["symbol"], "XLE")
        self.assertEqual(written_rows[0]["asset_class"], "etf")
        self.assertEqual(written_rows[0]["timeframe"], "1d")
        self.assertEqual(written_rows[1]["close"], 94.77)

        receipt = _read_json(receipt_path)
        self.assertEqual(receipt["receipt_type"], "historical_market_raw_write_receipt")
        self.assertEqual(receipt["status"], "written")
        self.assertEqual(receipt["source"], "alpha_vantage")
        self.assertEqual(receipt["symbol"], "XLE")
        self.assertEqual(receipt["asset_class"], "etf")
        self.assertEqual(receipt["record_count"], 2)
        self.assertEqual(receipt["batch_metadata"]["mode"], "smoke_test")

    def test_append_normalized_bars_multi_partition(self) -> None:
        bars = [
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 93.10,
                "high": 94.25,
                "low": 92.80,
                "close": 94.00,
                "volume": 12345678,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            },
            {
                "source": "alpha_vantage",
                "symbol": "CL",
                "asset_class": "commodity",
                "bar_timestamp": "2026-05-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 81.20,
                "high": 82.00,
                "low": 80.90,
                "close": 81.75,
                "volume": 998877,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            },
        ]

        results = self.store.append_normalized_bars(
            bars,
            receipt_id="raw-batch-002",
            source="alpha_vantage",
        )

        self.assertEqual(len(results), 2)

        output_paths = {Path(r.output_path) for r in results}
        self.assertIn(self.paths.raw_bar_month_file(asset_class="etf", symbol="XLE", year="2026", month="04"), output_paths)
        self.assertIn(self.paths.raw_bar_month_file(asset_class="commodity", symbol="CL", year="2026", month="05"), output_paths)

        xle_rows = self.store.read_month_file(asset_class="etf", symbol="XLE", year="2026", month="04")
        cl_rows = self.store.read_month_file(asset_class="commodity", symbol="CL", year="2026", month="05")

        self.assertEqual(len(xle_rows), 1)
        self.assertEqual(len(cl_rows), 1)
        self.assertEqual(xle_rows[0]["symbol"], "XLE")
        self.assertEqual(cl_rows[0]["symbol"], "CL")

    def test_append_is_append_only_for_same_month_file(self) -> None:
        first_batch = [
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 93.10,
                "high": 94.25,
                "low": 92.80,
                "close": 94.00,
                "volume": 12345678,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            }
        ]
        second_batch = [
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 94.00,
                "high": 94.90,
                "low": 93.60,
                "close": 94.77,
                "volume": 11335577,
                "fetched_at": "2026-04-06T13:05:00+00:00",
            }
        ]

        self.store.append_normalized_bars(first_batch, receipt_id="raw-batch-003")
        self.store.append_normalized_bars(second_batch, receipt_id="raw-batch-004")

        rows = self.store.read_month_file(asset_class="etf", symbol="XLE", year="2026", month="04")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["bar_timestamp"], "2026-04-01T00:00:00+00:00")
        self.assertEqual(rows[1]["bar_timestamp"], "2026-04-02T00:00:00+00:00")

    def test_invalid_bar_rejected_when_close_outside_range(self) -> None:
        invalid_bars = [
            {
                "source": "alpha_vantage",
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 93.10,
                "high": 94.25,
                "low": 92.80,
                "close": 95.00,
                "volume": 12345678,
                "fetched_at": "2026-04-06T13:00:00+00:00",
            }
        ]

        with self.assertRaises(ValueError):
            self.store.append_normalized_bars(invalid_bars, receipt_id="raw-batch-005")

    def test_empty_batch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.append_normalized_bars([], receipt_id="raw-batch-006")


if __name__ == "__main__":
    unittest.main()
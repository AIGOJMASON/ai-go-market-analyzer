from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from historical_market.derivation.pattern_pipeline import PatternPipeline
from historical_market.storage.curated_store import CuratedStore
from historical_market.storage.db_paths import HistoricalMarketPaths


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class TestPatternPipelineSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_pattern_pipeline_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()
        self.store = CuratedStore(paths=self.paths)
        self.pipeline = PatternPipeline(curated_store=self.store)

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_wires_setup_and_outcome_into_curated_store(self) -> None:
        event_id = "hist-xle-20260403-01"

        setup_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 99.5,
                "low": 96.5,
                "close": 97.5,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 97.8,
                "high": 99.8,
                "low": 97.4,
                "close": 98.8,
            },
        ]

        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-04T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 100.2,
                "low": 98.7,
                "close": 99.9,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-05T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 101.4,
                "low": 99.8,
                "close": 101.0,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-06T00:00:00+00:00",
                "timeframe": "1d",
                "open": 101.0,
                "high": 101.8,
                "low": 100.7,
                "close": 101.5,
            },
        ]

        result = self.pipeline.process_event(
            event_id=event_id,
            setup_bars=setup_bars,
            anchor_bar=setup_bars[-1],
            future_bars=future_bars,
            horizon_bars=3,
            outcome_notes="Pipeline smoke test.",
        )

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.setup_written)
        self.assertTrue(result.outcome_written)

        setup_artifact_path = Path(result.setup_write_result["artifact_path"])
        outcome_artifact_path = Path(result.outcome_write_result["artifact_path"])

        self.assertTrue(setup_artifact_path.exists())
        self.assertTrue(outcome_artifact_path.exists())

        setup_payload = _read_json(setup_artifact_path)
        outcome_payload = _read_json(outcome_artifact_path)

        self.assertEqual(setup_payload["artifact_type"], "historical_setup_pattern")
        self.assertEqual(setup_payload["setup_type"], "dip_rebound")
        self.assertEqual(outcome_payload["artifact_type"], "historical_outcome_event")
        self.assertEqual(outcome_payload["outcome_label"], "follow_through")
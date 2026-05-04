from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from historical_market.adapters.operator_translation_adapter import OperatorTranslationAdapter
from historical_market.derivation.pattern_pipeline import PatternPipeline
from historical_market.derivation.relationship_engine import RelationshipEngine
from historical_market.retrieval.historical_query_runtime import HistoricalQueryRuntime
from historical_market.services.historical_intelligence_service import HistoricalIntelligenceService
from historical_market.storage.curated_store import CuratedStore
from historical_market.storage.db_paths import HistoricalMarketPaths


class TestHistoricalIntelligenceServiceSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_hist_intel_service_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()

        self.store = CuratedStore(paths=self.paths)
        self.pipeline = PatternPipeline(curated_store=self.store)

        # Critical: inject query runtime bound to the SAME temp-path authority
        # used by the pipeline/store in this test.
        self.query_runtime = HistoricalQueryRuntime(paths=self.paths)
        self.service = HistoricalIntelligenceService(
            query_runtime=self.query_runtime,
            translation_adapter=OperatorTranslationAdapter(),
            relationship_engine=RelationshipEngine(),
        )

        event_id = "hist-xle-20260403-01"
        setup_bars = [
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "open": 99.0, "high": 99.5, "low": 96.5, "close": 97.5},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "open": 97.8, "high": 99.8, "low": 97.4, "close": 98.8},
        ]
        future_bars = [
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "open": 99.0, "high": 100.2, "low": 98.7, "close": 99.9},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "open": 100.0, "high": 101.4, "low": 99.8, "close": 101.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "open": 101.0, "high": 101.8, "low": 100.7, "close": 101.5},
        ]

        self.pipeline.process_event(
            event_id=event_id,
            setup_bars=setup_bars,
            anchor_bar=setup_bars[-1],
            future_bars=future_bars,
            horizon_bars=3,
            outcome_notes="Service smoke test.",
        )

        self.leader_bars = [
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 100.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 102.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 101.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 103.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 105.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 104.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 106.0},
        ]
        self.follower_bars = [
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 80.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 80.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 81.6},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 80.8},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 82.4},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 84.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 83.2},
        ]

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_build_historical_intelligence(self) -> None:
        result = self.service.build_historical_intelligence(
            setup_type="dip_rebound",
            event_id="hist-xle-20260403-01",
            leader_bars=self.leader_bars,
            follower_bars=self.follower_bars,
            max_lag_bars=2,
            min_overlap_points=4,
        )

        self.assertEqual(result.status, "ok")
        self.assertIsNotNone(result.setup_history_panel)
        self.assertIsNotNone(result.event_package_panel)
        self.assertIsNotNone(result.relationship_panel)

        assert result.setup_history_panel is not None
        assert result.event_package_panel is not None
        assert result.relationship_panel is not None

        self.assertEqual(result.setup_history_panel["panel_type"], "setup_history")
        self.assertEqual(result.event_package_panel["panel_type"], "event_package")
        self.assertEqual(result.relationship_panel["panel_type"], "relationship_history")

        self.assertEqual(result.event_package_panel["setup_type"], "dip_rebound")
        self.assertEqual(result.event_package_panel["outcome_label"], "follow_through")


if __name__ == "__main__":
    unittest.main()
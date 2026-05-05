from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from child_cores.market_analyzer_v1.refinement.historical_context_bridge import (
    MarketAnalyzerHistoricalContextBridge,
)
from historical_market.adapters.operator_translation_adapter import OperatorTranslationAdapter
from historical_market.derivation.pattern_pipeline import PatternPipeline
from historical_market.derivation.relationship_engine import RelationshipEngine
from historical_market.retrieval.historical_query_runtime import HistoricalQueryRuntime
from historical_market.services.historical_intelligence_service import HistoricalIntelligenceService
from historical_market.storage.curated_store import CuratedStore
from historical_market.storage.db_paths import HistoricalMarketPaths


class TestHistoricalContextBridgeSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_hist_context_bridge_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()

        self.store = CuratedStore(paths=self.paths)
        self.pipeline = PatternPipeline(curated_store=self.store)
        self.query_runtime = HistoricalQueryRuntime(paths=self.paths)
        self.historical_service = HistoricalIntelligenceService(
            query_runtime=self.query_runtime,
            translation_adapter=OperatorTranslationAdapter(),
            relationship_engine=RelationshipEngine(),
        )
        self.bridge = MarketAnalyzerHistoricalContextBridge(
            historical_intelligence_service=self.historical_service,
        )

        self.event_id = "hist-xle-20260403-01"

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

        self.pipeline.process_event(
            event_id=self.event_id,
            setup_bars=setup_bars,
            anchor_bar=setup_bars[-1],
            future_bars=future_bars,
            horizon_bars=3,
            outcome_notes="Bridge smoke test.",
        )

        self.recent_bars = setup_bars
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

    def test_build_refinement_payload(self) -> None:
        runtime_output = {
            "request_id": "ui-live-001",
            "core_id": "market_analyzer_v1",
            "route_mode": "pm_route",
            "mode": "advisory",
            "runtime_panel": {
                "headline": "Energy rebound after necessity shock",
                "market_regime": "normal",
                "event_theme": "energy_rebound",
                "macro_bias": "neutral",
            },
            "recommendation_panel": {
                "state": "present",
                "count": 1,
            },
        }

        result = self.bridge.build_refinement_payload(
            request_id="ui-live-001",
            runtime_output=runtime_output,
            recent_bars=self.recent_bars,
            event_id=self.event_id,
            leader_bars=self.leader_bars,
            follower_bars=self.follower_bars,
            max_lag_bars=2,
            min_overlap_points=4,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.setup_type, "dip_rebound")
        self.assertTrue(result.historical_context_present)

        payload = result.refinement_payload
        self.assertEqual(payload["artifact_type"], "market_analyzer_historical_context_refinement_payload")
        self.assertTrue(payload["setup_detection"]["detected"])
        self.assertEqual(payload["setup_detection"]["setup_type"], "dip_rebound")
        self.assertEqual(payload["historical_context"]["status"], "ok")
        self.assertIsNotNone(payload["historical_context"]["setup_history_panel"])
        self.assertIsNotNone(payload["historical_context"]["event_package_panel"])
        self.assertIsNotNone(payload["historical_context"]["relationship_panel"])
        self.assertTrue(payload["constraints"]["annotation_only"])
        self.assertFalse(payload["constraints"]["recommendation_mutation_allowed"])

    def test_attach_to_runtime_output(self) -> None:
        runtime_output = {
            "request_id": "ui-live-001",
            "core_id": "market_analyzer_v1",
            "route_mode": "pm_route",
            "mode": "advisory",
        }

        attached = self.bridge.attach_to_runtime_output(
            request_id="ui-live-001",
            runtime_output=runtime_output,
            recent_bars=self.recent_bars,
            event_id=self.event_id,
            leader_bars=self.leader_bars,
            follower_bars=self.follower_bars,
            max_lag_bars=2,
            min_overlap_points=4,
        )

        self.assertIn("historical_context_refinement", attached)
        self.assertIn("historical_context_panel", attached)
        self.assertEqual(attached["historical_context_refinement"]["artifact_type"], "market_analyzer_historical_context_refinement_payload")


if __name__ == "__main__":
    unittest.main()
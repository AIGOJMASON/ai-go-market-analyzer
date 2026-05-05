from __future__ import annotations

import unittest

from historical_market.derivation.relationship_engine import RelationshipEngine


class TestRelationshipEngineSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RelationshipEngine()

    def test_detects_correlated_relationship(self) -> None:
        leader = [
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 100.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 101.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 102.2},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 101.7},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 103.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 104.1},
        ]
        follower = [
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 50.7},
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 51.4},
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 51.1},
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 52.0},
            {"symbol": "OIH", "asset_class": "etf", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 52.8},
        ]

        result = self.engine.analyze_pair(leader_bars=leader, follower_bars=follower)

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.relationship_type, "correlated")
        self.assertEqual(result.leader_symbol, "XLE")
        self.assertEqual(result.follower_symbol, "OIH")

    def test_detects_lead_lag_relationship(self) -> None:
        leader = [
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 100.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 102.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 101.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 103.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 105.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 104.0},
            {"symbol": "XLE", "asset_class": "etf", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 106.0},
        ]
        follower = [
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 80.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 80.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 81.6},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 80.8},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 82.4},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 84.0},
            {"symbol": "CL", "asset_class": "commodity", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 83.2},
        ]

        result = self.engine.analyze_pair(
            leader_bars=leader,
            follower_bars=follower,
            max_lag_bars=2,
            min_overlap_points=4,
        )

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.relationship_type, "lead_lag")
        self.assertGreater(result.lag_bars, 0)

    def test_build_relationship_record_returns_none_when_not_detected(self) -> None:
        leader = [
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 100.0},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 101.2},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 100.4},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 101.0},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 100.7},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 101.5},
            {"symbol": "AAA", "asset_class": "equity", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 100.9},
        ]
        follower = [
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-01T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-02T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-03T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-04T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-05T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-06T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
            {"symbol": "BBB", "asset_class": "equity", "bar_timestamp": "2026-04-07T00:00:00+00:00", "timeframe": "1d", "close": 50.0},
        ]

        record = self.engine.build_relationship_record(
            leader_bars=leader,
            follower_bars=follower,
        )
        self.assertIsNone(record)


if __name__ == "__main__":
    unittest.main()
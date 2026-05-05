from __future__ import annotations

import unittest

from historical_market.derivation.setup_detector import SetupDetector


class TestSetupDetectorSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = SetupDetector()

    def test_detects_dip_rebound(self) -> None:
        bars = [
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

        result = self.detector.detect_latest_setup(bars)

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.setup_type, "dip_rebound")
        self.assertEqual(result.symbol, "XLE")
        self.assertEqual(result.asset_class, "etf")
        self.assertEqual(result.timeframe, "1d")
        self.assertGreater(result.confidence, 0.0)
        self.assertIn("drawdown_pct", result.supporting_features)
        self.assertIn("rebound_pct", result.supporting_features)

    def test_detects_breakout(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 101.0,
                "low": 99.5,
                "close": 100.4,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.3,
                "high": 101.2,
                "low": 99.8,
                "close": 100.9,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 101.0,
                "high": 102.4,
                "low": 100.8,
                "close": 102.0,
            },
        ]

        result = self.detector.detect_latest_setup(bars)

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.setup_type, "breakout")
        self.assertIn("breakout_pct", result.supporting_features)

    def test_detects_continuation(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 100.8,
                "low": 99.8,
                "close": 100.2,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.2,
                "high": 101.1,
                "low": 100.0,
                "close": 100.9,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.9,
                "high": 101.7,
                "low": 100.7,
                "close": 101.5,
            },
        ]

        result = self.detector.detect_latest_setup(bars)

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.setup_type, "continuation")
        self.assertIn("positive_steps_ratio", result.supporting_features)
        self.assertIn("net_move_pct", result.supporting_features)

    def test_detects_fade(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 101.0,
                "low": 99.5,
                "close": 100.6,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.7,
                "high": 101.5,
                "low": 100.3,
                "close": 101.2,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 101.7,
                "high": 101.8,
                "low": 100.2,
                "close": 100.5,
            },
        ]

        result = self.detector.detect_latest_setup(bars)

        self.assertEqual(result.status, "ok")
        self.assertTrue(result.detected)
        self.assertEqual(result.setup_type, "fade")
        self.assertIn("intraday_change_pct", result.supporting_features)

    def test_returns_no_detection_when_no_supported_setup(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 100.6,
                "low": 99.7,
                "close": 100.2,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.1,
                "high": 100.5,
                "low": 99.8,
                "close": 100.0,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 100.4,
                "low": 99.9,
                "close": 100.1,
            },
        ]

        result = self.detector.detect_latest_setup(bars)

        self.assertEqual(result.status, "ok")
        self.assertFalse(result.detected)
        self.assertIsNone(result.setup_type)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.supporting_features["reason"], "no_supported_setup_detected")

    def test_build_setup_pattern_record_returns_record_when_detected(self) -> None:
        bars = [
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

        record = self.detector.build_setup_pattern_record(
            event_id="hist-xle-20260403-01",
            bars=bars,
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["event_id"], "hist-xle-20260403-01")
        self.assertEqual(record["setup_type"], "dip_rebound")
        self.assertEqual(record["pattern_id"], "hist-xle-20260403-01-dip_rebound")
        self.assertIn("supporting_features", record)

    def test_build_setup_pattern_record_returns_none_when_not_detected(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 100.6,
                "low": 99.7,
                "close": 100.2,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.1,
                "high": 100.5,
                "low": 99.8,
                "close": 100.0,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 100.4,
                "low": 99.9,
                "close": 100.1,
            },
        ]

        record = self.detector.build_setup_pattern_record(
            event_id="hist-xle-20260403-02",
            bars=bars,
        )

        self.assertIsNone(record)

    def test_rejects_non_daily_timeframe(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T14:30:00+00:00",
                "timeframe": "5m",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T14:35:00+00:00",
                "timeframe": "5m",
                "open": 100.5,
                "high": 101.1,
                "low": 100.3,
                "close": 100.9,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T14:40:00+00:00",
                "timeframe": "5m",
                "open": 100.9,
                "high": 101.4,
                "low": 100.7,
                "close": 101.2,
            },
        ]

        with self.assertRaises(ValueError):
            self.detector.detect_latest_setup(bars)

    def test_rejects_when_not_enough_bars(self) -> None:
        bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-01T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-02T00:00:00+00:00",
                "timeframe": "1d",
                "open": 100.5,
                "high": 101.2,
                "low": 100.1,
                "close": 100.8,
            },
        ]

        with self.assertRaises(ValueError):
            self.detector.detect_latest_setup(bars)


if __name__ == "__main__":
    unittest.main()
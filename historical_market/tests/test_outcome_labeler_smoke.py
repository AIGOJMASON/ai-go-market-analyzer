from __future__ import annotations

import unittest

from historical_market.derivation.outcome_labeler import OutcomeLabeler


class TestOutcomeLabelerSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.labeler = OutcomeLabeler()
        self.anchor_bar = {
            "symbol": "XLE",
            "asset_class": "etf",
            "bar_timestamp": "2026-04-03T00:00:00+00:00",
            "timeframe": "1d",
            "open": 97.8,
            "high": 99.8,
            "low": 97.4,
            "close": 98.8,
        }

    def test_labels_follow_through(self) -> None:
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

        result = self.labeler.label_outcome(
            anchor_bar=self.anchor_bar,
            future_bars=future_bars,
            horizon_bars=3,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.outcome_label, "follow_through")
        self.assertEqual(result.symbol, "XLE")
        self.assertEqual(result.asset_class, "etf")
        self.assertEqual(result.timeframe, "1d")
        self.assertEqual(result.horizon_bars, 3)
        self.assertGreater(result.close_return_pct, 1.5)
        self.assertGreater(result.max_favorable_excursion_pct, 1.5)

    def test_labels_failure(self) -> None:
        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-04T00:00:00+00:00",
                "timeframe": "1d",
                "open": 98.5,
                "high": 98.9,
                "low": 97.2,
                "close": 97.6,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-05T00:00:00+00:00",
                "timeframe": "1d",
                "open": 97.4,
                "high": 97.8,
                "low": 96.5,
                "close": 96.9,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-06T00:00:00+00:00",
                "timeframe": "1d",
                "open": 96.8,
                "high": 97.0,
                "low": 95.8,
                "close": 96.0,
            },
        ]

        result = self.labeler.label_outcome(
            anchor_bar=self.anchor_bar,
            future_bars=future_bars,
            horizon_bars=3,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.outcome_label, "failure")
        self.assertLess(result.close_return_pct, -1.0)
        self.assertLess(result.max_adverse_excursion_pct, -1.0)

    def test_labels_stall(self) -> None:
        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-04T00:00:00+00:00",
                "timeframe": "1d",
                "open": 98.7,
                "high": 99.5,
                "low": 98.3,
                "close": 99.1,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-05T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 99.6,
                "low": 98.6,
                "close": 99.0,
            },
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-06T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 99.7,
                "low": 98.7,
                "close": 99.2,
            },
        ]

        result = self.labeler.label_outcome(
            anchor_bar=self.anchor_bar,
            future_bars=future_bars,
            horizon_bars=3,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.outcome_label, "stall")
        self.assertGreater(result.close_return_pct, -1.0)
        self.assertLess(result.close_return_pct, 1.5)

    def test_build_outcome_event_record(self) -> None:
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

        record = self.labeler.build_outcome_event_record(
            event_id="hist-xle-20260403-01",
            anchor_bar=self.anchor_bar,
            future_bars=future_bars,
            horizon_bars=3,
            notes="Smoke test outcome record.",
        )

        self.assertEqual(record["event_id"], "hist-xle-20260403-01")
        self.assertEqual(record["outcome_id"], "hist-xle-20260403-01-h03")
        self.assertEqual(record["outcome_label"], "follow_through")
        self.assertEqual(record["horizon_bars"], 3)
        self.assertIn("supporting_features", record)
        self.assertEqual(record["notes"], "Smoke test outcome record.")

    def test_rejects_non_daily_timeframe(self) -> None:
        anchor_bar = {
            "symbol": "XLE",
            "asset_class": "etf",
            "bar_timestamp": "2026-04-03T14:30:00+00:00",
            "timeframe": "5m",
            "open": 97.8,
            "high": 99.8,
            "low": 97.4,
            "close": 98.8,
        }
        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T14:35:00+00:00",
                "timeframe": "5m",
                "open": 98.9,
                "high": 99.2,
                "low": 98.7,
                "close": 99.0,
            }
        ]

        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=anchor_bar,
                future_bars=future_bars,
                horizon_bars=1,
            )

    def test_rejects_symbol_mismatch(self) -> None:
        future_bars = [
            {
                "symbol": "CL",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-04T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 100.2,
                "low": 98.7,
                "close": 99.9,
            }
        ]

        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=self.anchor_bar,
                future_bars=future_bars,
                horizon_bars=1,
            )

    def test_rejects_asset_class_mismatch(self) -> None:
        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "commodity",
                "bar_timestamp": "2026-04-04T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 100.2,
                "low": 98.7,
                "close": 99.9,
            }
        ]

        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=self.anchor_bar,
                future_bars=future_bars,
                horizon_bars=1,
            )

    def test_rejects_future_bar_not_after_anchor(self) -> None:
        future_bars = [
            {
                "symbol": "XLE",
                "asset_class": "etf",
                "bar_timestamp": "2026-04-03T00:00:00+00:00",
                "timeframe": "1d",
                "open": 99.0,
                "high": 100.2,
                "low": 98.7,
                "close": 99.9,
            }
        ]

        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=self.anchor_bar,
                future_bars=future_bars,
                horizon_bars=1,
            )

    def test_rejects_empty_future_bars(self) -> None:
        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=self.anchor_bar,
                future_bars=[],
                horizon_bars=1,
            )

    def test_rejects_invalid_horizon(self) -> None:
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
            }
        ]

        with self.assertRaises(ValueError):
            self.labeler.label_outcome(
                anchor_bar=self.anchor_bar,
                future_bars=future_bars,
                horizon_bars=0,
            )


if __name__ == "__main__":
    unittest.main()
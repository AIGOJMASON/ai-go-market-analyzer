from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from historical_market.storage.curated_store import CuratedStore
from historical_market.storage.db_paths import HistoricalMarketPaths


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


class TestCuratedStoreSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ai_go_hist_market_")
        self.project_root = Path(self._tmpdir) / "AI_GO"
        self.project_root.mkdir(parents=True, exist_ok=True)

        self.paths = HistoricalMarketPaths(project_root=self.project_root)
        self.paths.ensure_all()
        self.store = CuratedStore(paths=self.paths)

        self.event_id = "hist-xle-20260403-01"
        self.intake_timestamp = "2026-04-03T00:00:00+00:00"
        self.merge_timestamp = "2026-04-03T15:30:00+00:00"
        self.outcome_timestamp = "2026-04-10T00:00:00+00:00"

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_smoke_intake_merge_outcome_write_flow(self) -> None:
        intake_result = self.store.write_intake_event(
            {
                "event_id": self.event_id,
                "intake_timestamp": self.intake_timestamp,
                "symbol": "XLE",
                "asset_class": "etf",
                "timeframe": "1d",
                "signal_seed": "daily_bar_observation",
                "source_ref": "alpha_vantage:XLE:2026-04-03",
                "headline": "Energy rebound after necessity shock",
                "raw_signal": {"close": 94.77},
                "normalized_signal": {"theme": "energy_rebound"},
            }
        )

        self.assertEqual(intake_result.status, "written")
        intake_artifact_path = Path(intake_result.artifact_path)
        intake_receipt_path = Path(intake_result.receipt_path)
        intake_index_path = Path(intake_result.index_path)

        self.assertTrue(intake_artifact_path.exists())
        self.assertTrue(intake_receipt_path.exists())
        self.assertTrue(intake_index_path.exists())

        intake_artifact = _read_json(intake_artifact_path)
        self.assertEqual(intake_artifact["event_id"], self.event_id)
        self.assertEqual(intake_artifact["artifact_type"], "historical_intake_event")
        self.assertEqual(intake_artifact["symbol"], "XLE")

        intake_receipt = _read_json(intake_receipt_path)
        self.assertEqual(intake_receipt["receipt_type"], "historical_market_curated_write_receipt")
        self.assertEqual(intake_receipt["artifact_type"], "historical_intake_event")
        self.assertEqual(intake_receipt["artifact_id"], self.event_id)

        intake_index_rows = _read_jsonl(intake_index_path)
        self.assertEqual(len(intake_index_rows), 1)
        self.assertEqual(intake_index_rows[0]["artifact_type"], "historical_intake_event")
        self.assertEqual(intake_index_rows[0]["event_id"], self.event_id)

        merge_id = "merge-xle-20260403-01"
        merge_result = self.store.write_merge_event(
            {
                "merge_id": merge_id,
                "event_id": self.event_id,
                "merge_timestamp": self.merge_timestamp,
                "merge_status": "attached",
                "attached_memory_refs": ["mem-xle-pattern-001"],
                "merge_context": {"historical_match_count": 3},
                "notes": "Historical memory attached after governed processing.",
            }
        )

        self.assertEqual(merge_result.status, "written")
        merge_artifact_path = Path(merge_result.artifact_path)
        merge_receipt_path = Path(merge_result.receipt_path)
        merge_index_path = Path(merge_result.index_path)

        self.assertTrue(merge_artifact_path.exists())
        self.assertTrue(merge_receipt_path.exists())
        self.assertTrue(merge_index_path.exists())

        merge_artifact = _read_json(merge_artifact_path)
        self.assertEqual(merge_artifact["merge_id"], merge_id)
        self.assertEqual(merge_artifact["event_id"], self.event_id)
        self.assertEqual(merge_artifact["artifact_type"], "historical_merge_event")

        merge_index_rows = _read_jsonl(merge_index_path)
        self.assertEqual(len(merge_index_rows), 1)
        self.assertEqual(merge_index_rows[0]["artifact_type"], "historical_merge_event")
        self.assertEqual(merge_index_rows[0]["event_id"], self.event_id)

        outcome_id = "outcome-xle-20260403-h05"
        outcome_result = self.store.write_outcome_event(
            {
                "outcome_id": outcome_id,
                "event_id": self.event_id,
                "outcome_timestamp": self.outcome_timestamp,
                "outcome_label": "follow_through",
                "horizon_bars": 5,
                "max_favorable_excursion_pct": 2.8,
                "max_adverse_excursion_pct": -0.9,
                "close_return_pct": 2.1,
                "notes": "Five-bar follow-through confirmed.",
            }
        )

        self.assertEqual(outcome_result.status, "written")
        outcome_artifact_path = Path(outcome_result.artifact_path)
        outcome_receipt_path = Path(outcome_result.receipt_path)
        outcome_index_path = Path(outcome_result.index_path)

        self.assertTrue(outcome_artifact_path.exists())
        self.assertTrue(outcome_receipt_path.exists())
        self.assertTrue(outcome_index_path.exists())

        outcome_artifact = _read_json(outcome_artifact_path)
        self.assertEqual(outcome_artifact["outcome_id"], outcome_id)
        self.assertEqual(outcome_artifact["event_id"], self.event_id)
        self.assertEqual(outcome_artifact["artifact_type"], "historical_outcome_event")

        outcome_index_rows = _read_jsonl(outcome_index_path)
        self.assertEqual(len(outcome_index_rows), 1)
        self.assertEqual(outcome_index_rows[0]["artifact_type"], "historical_outcome_event")
        self.assertEqual(outcome_index_rows[0]["event_id"], self.event_id)

        event_spine_path = self.paths.event_spine_file(self.event_id)
        self.assertTrue(event_spine_path.exists())

        event_spine = _read_json(event_spine_path)
        self.assertEqual(event_spine["event_id"], self.event_id)
        self.assertEqual(len(event_spine["records"]), 3)

        artifact_types = [row["artifact_type"] for row in event_spine["records"]]
        self.assertEqual(
            artifact_types,
            [
                "historical_intake_event",
                "historical_merge_event",
                "historical_outcome_event",
            ],
        )

    def test_duplicate_intake_write_fails(self) -> None:
        payload = {
            "event_id": self.event_id,
            "intake_timestamp": self.intake_timestamp,
            "symbol": "XLE",
            "asset_class": "etf",
            "timeframe": "1d",
            "signal_seed": "daily_bar_observation",
        }

        first = self.store.write_intake_event(payload)
        self.assertEqual(first.status, "written")

        with self.assertRaises(FileExistsError):
            self.store.write_intake_event(payload)

    def test_read_artifact_round_trip(self) -> None:
        self.store.write_intake_event(
            {
                "event_id": self.event_id,
                "intake_timestamp": self.intake_timestamp,
                "symbol": "XLE",
                "asset_class": "etf",
                "timeframe": "1d",
                "signal_seed": "daily_bar_observation",
                "source_ref": "alpha_vantage:XLE:2026-04-03",
            }
        )

        loaded = self.store.read_artifact("historical_intake_event", self.event_id)
        self.assertEqual(loaded["event_id"], self.event_id)
        self.assertEqual(loaded["symbol"], "XLE")
        self.assertEqual(loaded["artifact_type"], "historical_intake_event")


if __name__ == "__main__":
    unittest.main()
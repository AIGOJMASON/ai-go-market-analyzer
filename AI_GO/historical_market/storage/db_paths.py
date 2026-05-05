from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


def _default_project_root() -> Path:
    """
    Resolve the AI_GO project root from this file location.

    Expected path:
        AI_GO/historical_market/storage/db_paths.py

    parents[0] = storage
    parents[1] = historical_market
    parents[2] = AI_GO
    """
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class HistoricalMarketPaths:
    """
    Single path authority for the Historical Market subsystem.

    This class defines the append-only storage layout for:
    - raw market history
    - curated historical records
    - indexes
    - write receipts
    """

    project_root: Path | None = None

    def __post_init__(self) -> None:
        root = self.project_root or _default_project_root()
        object.__setattr__(self, "project_root", root)

        state_root = root / "state" / "historical_market"
        object.__setattr__(self, "state_root", state_root)

        raw_root = state_root / "raw"
        curated_root = state_root / "curated"

        object.__setattr__(self, "raw_root", raw_root)
        object.__setattr__(self, "curated_root", curated_root)

        object.__setattr__(self, "raw_bars_dir", raw_root / "bars")
        object.__setattr__(self, "raw_fetch_receipts_dir", raw_root / "fetch_receipts")

        object.__setattr__(self, "intake_events_dir", curated_root / "intake_events")
        object.__setattr__(self, "merge_events_dir", curated_root / "merge_events")
        object.__setattr__(self, "outcome_events_dir", curated_root / "outcome_events")
        object.__setattr__(self, "setup_patterns_dir", curated_root / "setup_patterns")
        object.__setattr__(self, "asset_relationships_dir", curated_root / "asset_relationships")
        object.__setattr__(self, "indexes_dir", curated_root / "indexes")
        object.__setattr__(self, "write_receipts_dir", curated_root / "write_receipts")

    @property
    def all_directories(self) -> List[Path]:
        return [
            self.state_root,
            self.raw_root,
            self.curated_root,
            self.raw_bars_dir,
            self.raw_fetch_receipts_dir,
            self.intake_events_dir,
            self.merge_events_dir,
            self.outcome_events_dir,
            self.setup_patterns_dir,
            self.asset_relationships_dir,
            self.indexes_dir,
            self.write_receipts_dir,
            self.indexes_dir / "intake_events",
            self.indexes_dir / "merge_events",
            self.indexes_dir / "outcome_events",
            self.indexes_dir / "setup_patterns",
            self.indexes_dir / "asset_relationships",
            self.indexes_dir / "event_spine",
            self.write_receipts_dir / "intake_events",
            self.write_receipts_dir / "merge_events",
            self.write_receipts_dir / "outcome_events",
            self.write_receipts_dir / "setup_patterns",
            self.write_receipts_dir / "asset_relationships",
        ]

    def ensure_all(self) -> None:
        for directory in self.all_directories:
            directory.mkdir(parents=True, exist_ok=True)

    def raw_bar_month_file(
        self,
        *,
        asset_class: str,
        symbol: str,
        year: str | int,
        month: str | int,
    ) -> Path:
        asset_class_clean = self._clean_segment(asset_class, lower=True)
        symbol_clean = self._clean_segment(symbol, upper=True)
        year_clean = self._normalize_year(year)
        month_clean = self._normalize_month(month)

        return (
            self.raw_bars_dir
            / asset_class_clean
            / symbol_clean
            / year_clean
            / f"{month_clean}.jsonl"
        )

    def raw_fetch_receipt_file(self, receipt_id: str) -> Path:
        receipt_id_clean = self._clean_segment(receipt_id, lower=False)
        return self.raw_fetch_receipts_dir / f"{receipt_id_clean}.receipt.json"

    def intake_event_file(self, event_id: str) -> Path:
        return self.intake_events_dir / f"{self._clean_segment(event_id, lower=False)}.json"

    def merge_event_file(self, merge_id: str) -> Path:
        return self.merge_events_dir / f"{self._clean_segment(merge_id, lower=False)}.json"

    def outcome_event_file(self, outcome_id: str) -> Path:
        return self.outcome_events_dir / f"{self._clean_segment(outcome_id, lower=False)}.json"

    def setup_pattern_file(self, pattern_id: str) -> Path:
        return self.setup_patterns_dir / f"{self._clean_segment(pattern_id, lower=False)}.json"

    def asset_relationship_file(self, relationship_id: str) -> Path:
        return self.asset_relationships_dir / f"{self._clean_segment(relationship_id, lower=False)}.json"

    def intake_index_file(self, year_month: str) -> Path:
        return self.indexes_dir / "intake_events" / f"{self._normalize_year_month(year_month)}.jsonl"

    def merge_index_file(self, year_month: str) -> Path:
        return self.indexes_dir / "merge_events" / f"{self._normalize_year_month(year_month)}.jsonl"

    def outcome_index_file(self, year_month: str) -> Path:
        return self.indexes_dir / "outcome_events" / f"{self._normalize_year_month(year_month)}.jsonl"

    def setup_pattern_index_file(self, year_month: str) -> Path:
        return self.indexes_dir / "setup_patterns" / f"{self._normalize_year_month(year_month)}.jsonl"

    def asset_relationship_index_file(self, year_month: str) -> Path:
        return self.indexes_dir / "asset_relationships" / f"{self._normalize_year_month(year_month)}.jsonl"

    def event_spine_file(self, event_id: str) -> Path:
        return self.indexes_dir / "event_spine" / f"{self._clean_segment(event_id, lower=False)}.json"

    def intake_receipt_file(self, event_id: str) -> Path:
        return self.write_receipts_dir / "intake_events" / f"{self._clean_segment(event_id, lower=False)}.receipt.json"

    def merge_receipt_file(self, merge_id: str) -> Path:
        return self.write_receipts_dir / "merge_events" / f"{self._clean_segment(merge_id, lower=False)}.receipt.json"

    def outcome_receipt_file(self, outcome_id: str) -> Path:
        return self.write_receipts_dir / "outcome_events" / f"{self._clean_segment(outcome_id, lower=False)}.receipt.json"

    def setup_pattern_receipt_file(self, pattern_id: str) -> Path:
        return self.write_receipts_dir / "setup_patterns" / f"{self._clean_segment(pattern_id, lower=False)}.receipt.json"

    def asset_relationship_receipt_file(self, relationship_id: str) -> Path:
        return self.write_receipts_dir / "asset_relationships" / f"{self._clean_segment(relationship_id, lower=False)}.receipt.json"

    def as_dict(self) -> Dict[str, str]:
        return {
            "project_root": str(self.project_root),
            "state_root": str(self.state_root),
            "raw_root": str(self.raw_root),
            "curated_root": str(self.curated_root),
            "raw_bars_dir": str(self.raw_bars_dir),
            "raw_fetch_receipts_dir": str(self.raw_fetch_receipts_dir),
            "intake_events_dir": str(self.intake_events_dir),
            "merge_events_dir": str(self.merge_events_dir),
            "outcome_events_dir": str(self.outcome_events_dir),
            "setup_patterns_dir": str(self.setup_patterns_dir),
            "asset_relationships_dir": str(self.asset_relationships_dir),
            "indexes_dir": str(self.indexes_dir),
            "write_receipts_dir": str(self.write_receipts_dir),
        }

    def _clean_segment(self, value: str, *, lower: bool = False, upper: bool = False) -> str:
        text = str(value).strip()
        if not text:
            raise ValueError("path segment must not be empty")

        allowed_chars = []
        for ch in text:
            if ch.isalnum() or ch in ("-", "_", "."):
                allowed_chars.append(ch)
            else:
                allowed_chars.append("_")

        cleaned = "".join(allowed_chars)

        if lower:
            cleaned = cleaned.lower()
        if upper:
            cleaned = cleaned.upper()

        if cleaned in {".", ".."}:
            raise ValueError("invalid path segment")
        return cleaned

    def _normalize_year(self, year: str | int) -> str:
        text = str(year).strip()
        if len(text) != 4 or not text.isdigit():
            raise ValueError(f"invalid year: {year}")
        return text

    def _normalize_month(self, month: str | int) -> str:
        text = str(month).strip()
        if not text.isdigit():
            raise ValueError(f"invalid month: {month}")
        value = int(text)
        if value < 1 or value > 12:
            raise ValueError(f"invalid month: {month}")
        return f"{value:02d}"

    def _normalize_year_month(self, year_month: str) -> str:
        text = str(year_month).strip()
        if len(text) != 7 or text[4] != "-":
            raise ValueError(f"invalid year-month format: {year_month}")
        year = text[:4]
        month = text[5:7]
        return f"{self._normalize_year(year)}-{self._normalize_month(month)}"


_default_paths: Optional[HistoricalMarketPaths] = None


def get_historical_market_paths() -> HistoricalMarketPaths:
    global _default_paths
    if _default_paths is None:
        _default_paths = HistoricalMarketPaths()
    return _default_paths


def ensure_historical_market_paths() -> HistoricalMarketPaths:
    paths = get_historical_market_paths()
    paths.ensure_all()
    return paths
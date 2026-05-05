# AI_GO/historical_market/storage/__init__.py

from __future__ import annotations

"""
Historical Market storage package.

Northstar 6A posture:
- This package initializer is read-only.
- It performs no persistence.
- All historical market writes must route through governed_write_json.
- Required mutation fields for writer modules:
  mutation_class
  persistence_type
  authority_metadata
"""

from AI_GO.historical_market.storage.db_paths import HistoricalMarketPaths
from AI_GO.historical_market.storage.raw_store import RawStore, RawBarWriteResult
from AI_GO.historical_market.storage.curated_store import CuratedStore, CuratedWriteResult

__all__ = [
    "HistoricalMarketPaths",
    "RawStore",
    "RawBarWriteResult",
    "CuratedStore",
    "CuratedWriteResult",
]
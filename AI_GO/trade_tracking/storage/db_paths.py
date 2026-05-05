from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def trade_tracking_root() -> Path:
    return _project_root() / "state" / "trade_tracking"


def current_dir() -> Path:
    return trade_tracking_root() / "current"


def db_dir() -> Path:
    return trade_tracking_root() / "db"


def events_dir() -> Path:
    return db_dir() / "events"


def indexes_dir() -> Path:
    return db_dir() / "indexes"


def receipts_dir() -> Path:
    return db_dir() / "receipts"


def monthly_events_dir(timestamp: str) -> Path:
    year_month = timestamp[:7]
    return events_dir() / year_month


def ensure_trade_tracking_dirs() -> None:
    for path in [
        trade_tracking_root(),
        current_dir(),
        db_dir(),
        events_dir(),
        indexes_dir(),
        receipts_dir(),
    ]:
        path.mkdir(parents=True, exist_ok=True)
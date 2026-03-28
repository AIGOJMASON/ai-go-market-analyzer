from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_DIR = Path("AI_GO/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "market_analyzer_requests.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_request_event(*args: Any, **kwargs: Any) -> None:
    if args and isinstance(args[0], dict):
        record = dict(args[0])
    elif args:
        raise TypeError("log_request_event accepts either a single dict or keyword arguments only")
    else:
        record = dict(kwargs)

    record.setdefault("logged_at", _utc_now_iso())

    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
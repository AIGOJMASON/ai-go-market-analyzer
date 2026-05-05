from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.state_runtime.state_paths import logs_root


class LogRetrievalError(ValueError):
    pass


def _market_analyzer_log_path() -> Path:
    return logs_root() / "market_analyzer_requests.jsonl"


def _safe_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return parsed


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean:
            continue
        try:
            payload = json.loads(clean)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)

    return records


def list_market_analyzer_request_logs(
    *,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    safe_limit = max(1, min(_safe_int(limit, 100), 1000))
    safe_offset = max(0, _safe_int(offset, 0))

    path = _market_analyzer_log_path()
    records = _load_jsonl(path)
    records.reverse()

    paged = records[safe_offset: safe_offset + safe_limit]

    return {
        "status": "ok",
        "artifact_type": "market_analyzer_request_log_index",
        "log_path": str(path),
        "count": len(paged),
        "total": len(records),
        "limit": safe_limit,
        "offset": safe_offset,
        "items": paged,
    }


def get_recent_request_logs(limit: int = 100) -> Dict[str, Any]:
    return list_market_analyzer_request_logs(limit=limit, offset=0)


def read_request_log_file() -> Dict[str, Any]:
    path = _market_analyzer_log_path()

    return {
        "status": "ok" if path.exists() else "missing",
        "path": str(path),
        "items": _load_jsonl(path),
    }
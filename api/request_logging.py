from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


_LOG_DIR = Path("AI_GO/logs")
_LOG_FILE = _LOG_DIR / "market_analyzer_requests.jsonl"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_log_dir() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


def _safe_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def build_request_log_entry(
    *,
    endpoint: str,
    request_id: Optional[str],
    case_id: Optional[str],
    auth_status: str,
    response_status: int,
    route_mode: Optional[str] = None,
    receipt_id: Optional[str] = None,
    detail: Optional[str] = None,
    client_ip: Optional[str] = None,
    core_id: str = "market_analyzer_v1",
    service: str = "market_analyzer_api",
) -> Dict[str, Any]:
    return {
        "timestamp": _utc_timestamp(),
        "service": service,
        "core_id": core_id,
        "endpoint": endpoint,
        "request_id": _safe_text(request_id),
        "case_id": _safe_text(case_id),
        "client_ip": _safe_text(client_ip),
        "auth_status": auth_status,
        "response_status": int(response_status),
        "route_mode": _safe_text(route_mode),
        "receipt_id": _safe_text(receipt_id),
        "detail": _safe_text(detail),
    }


def append_request_log(entry: Dict[str, Any]) -> None:
    _ensure_log_dir()
    with _LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
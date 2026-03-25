import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


LOG_PATH = Path("logs/market_analyzer_requests.jsonl")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_request_log(event_type: str, payload: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": _utc_now_iso(),
        "event_type": event_type,
        **payload,
    }

    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_base_log_payload(
    *,
    request_id: Optional[str],
    case_id: Optional[str],
    auth_status: Optional[str],
    response_status: Optional[int],
    route_mode: Optional[str],
    receipt_id: Optional[str],
    client_ip: Optional[str],
    api_key_id: Optional[str],
    rate_limit_bucket_id: Optional[str] = None,
    rate_limit_count: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "request_id": request_id,
        "case_id": case_id,
        "auth_status": auth_status,
        "response_status": response_status,
        "route_mode": route_mode,
        "receipt_id": receipt_id,
        "client_ip": client_ip,
        "api_key_id": api_key_id,
        "rate_limit_bucket_id": rate_limit_bucket_id,
        "rate_limit_count": rate_limit_count,
    }
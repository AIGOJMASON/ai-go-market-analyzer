from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


LOG_PATH = Path("logs/market_analyzer_requests.jsonl")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_request_log(*args: Any, **kwargs: Any) -> None:
    """
    Flexible logging entrypoint.

    Supports:
    1. append_request_log("event_type", payload_dict)
    2. append_request_log(event_dict)

    This ensures compatibility with:
    - legacy logging calls
    - new auth / rate limit logging
    """

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record: Dict[str, Any]

    # --- NEW STYLE: append_request_log(event_dict) ---
    if len(args) == 1 and isinstance(args[0], dict):
        record = dict(args[0])

        # ensure required fields
        record.setdefault("event_type", "unknown_event")

    # --- LEGACY STYLE: append_request_log(event_type, payload) ---
    elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], dict):
        event_type = args[0]
        payload = args[1]

        record = {
            "event_type": event_type,
            **payload,
        }

    else:
        raise RuntimeError(
            "Invalid append_request_log usage. "
            "Expected (event_type, payload) or (event_dict)."
        )

    # --- normalize timestamp ---
    record.setdefault("timestamp", _utc_now_iso())

    # --- write ---
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
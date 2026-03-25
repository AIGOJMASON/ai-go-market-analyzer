import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Request


RECEIPTS_DIR = Path("receipts/market_analyzer_v1")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def generate_receipt_id(core_id: str) -> str:
    timestamp = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid4().hex[:10]
    return f"rcpt_{core_id}_{timestamp}_{nonce}"


def build_run_receipt(
    *,
    request: Request,
    request_id: Optional[str],
    case_id: Optional[str],
    api_key_id: Optional[str],
    route_mode: str,
    core_id: str,
    endpoint: str,
    raw_mode: bool,
) -> Dict[str, Any]:
    receipt_id = generate_receipt_id(core_id)

    return {
        "receipt_id": receipt_id,
        "artifact_type": "market_analyzer_run_receipt",
        "artifact_version": "v1",
        "created_at": _utc_now_iso(),
        "core_id": core_id,
        "route_mode": route_mode,
        "endpoint": endpoint,
        "request": {
            "request_id": request_id,
            "case_id": case_id,
            "raw_mode": raw_mode,
        },
        "governance": {
            "mode": "advisory",
            "execution_allowed": False,
            "approval_required": True,
        },
        "auth_context": {
            "auth_status": getattr(request.state, "auth_status", None),
            "api_key_id": api_key_id,
            "client_ip": _client_ip(request),
        },
        "rate_limit_context": {
            "bucket_id": getattr(request.state, "rate_limit_bucket_id", None),
            "count": getattr(request.state, "rate_limit_count", None),
            "limit": getattr(request.state, "rate_limit_limit", None),
            "window_seconds": getattr(request.state, "rate_limit_window_seconds", None),
        },
        "lineage": {
            "source_surface": "market_analyzer_api",
            "upstream_authority": "pm_route",
            "watcher_status": "pending",
            "watcher_ready": True,
        },
    }


def persist_receipt(receipt: Dict[str, Any]) -> Path:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    receipt_id = receipt["receipt_id"]
    path = RECEIPTS_DIR / f"{receipt_id}.json"

    with path.open("w", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)

    return path
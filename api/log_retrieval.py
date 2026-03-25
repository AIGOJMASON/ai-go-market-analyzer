from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUEST_LOG_PATH = Path("logs/market_analyzer_requests.jsonl")


class LogRetrievalError(Exception):
    """Raised when request-log retrieval cannot be completed lawfully."""


def _load_log_rows() -> List[Dict[str, Any]]:
    if not REQUEST_LOG_PATH.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with REQUEST_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LogRetrievalError("request_log_decode_failed") from exc
            if isinstance(item, dict):
                rows.append(item)
    return rows


def _apply_filters(
    rows: List[Dict[str, Any]],
    request_id: Optional[str] = None,
    case_id: Optional[str] = None,
    api_key_id: Optional[str] = None,
    auth_status: Optional[str] = None,
    event_type: Optional[str] = None,
    route_mode: Optional[str] = None,
    response_status: Optional[int] = None,
) -> List[Dict[str, Any]]:
    filtered = rows

    if request_id:
        filtered = [row for row in filtered if row.get("request_id") == request_id]
    if case_id:
        filtered = [row for row in filtered if row.get("case_id") == case_id]
    if api_key_id:
        filtered = [row for row in filtered if row.get("api_key_id") == api_key_id]
    if auth_status:
        filtered = [row for row in filtered if row.get("auth_status") == auth_status]
    if event_type:
        filtered = [row for row in filtered if row.get("event_type") == event_type]
    if route_mode:
        filtered = [row for row in filtered if row.get("route_mode") == route_mode]
    if response_status is not None:
        filtered = [
            row for row in filtered if row.get("response_status") == response_status
        ]

    return filtered


def list_request_logs(
    request_id: Optional[str] = None,
    case_id: Optional[str] = None,
    api_key_id: Optional[str] = None,
    auth_status: Optional[str] = None,
    event_type: Optional[str] = None,
    route_mode: Optional[str] = None,
    response_status: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1 or limit > 200:
        raise LogRetrievalError("limit_out_of_bounds")
    if offset < 0:
        raise LogRetrievalError("offset_out_of_bounds")

    rows = _load_log_rows()
    rows = list(reversed(rows))

    filtered = _apply_filters(
        rows=rows,
        request_id=request_id,
        case_id=case_id,
        api_key_id=api_key_id,
        auth_status=auth_status,
        event_type=event_type,
        route_mode=route_mode,
        response_status=response_status,
    )

    total = len(filtered)
    page = filtered[offset : offset + limit]

    return {
        "artifact_type": "market_analyzer_request_log_view",
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": page,
    }


def get_request_log_by_request_id(request_id: str) -> Dict[str, Any]:
    result = list_request_logs(request_id=request_id, limit=200, offset=0)
    return {
        "artifact_type": "market_analyzer_request_log_detail",
        "request_id": request_id,
        "match_count": result["total"],
        "results": result["results"],
    }
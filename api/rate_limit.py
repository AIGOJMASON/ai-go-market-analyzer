from __future__ import annotations

import os
import threading
import time
from collections import deque
from hashlib import sha256
from typing import Deque, Dict, Tuple

from fastapi import Header, HTTPException, Request, status

from AI_GO.api.request_logging import append_request_log, build_request_log_entry


_BUCKETS: Dict[Tuple[str, str, str], Deque[float]] = {}
_LOCK = threading.Lock()


def _get_limit() -> int:
    raw_value = os.getenv("AI_GO_RATE_LIMIT_REQUESTS", "10").strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server_rate_limit_not_configured",
        ) from exc

    if value <= 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server_rate_limit_not_configured",
        )

    return value


def _get_window_seconds() -> int:
    raw_value = os.getenv("AI_GO_RATE_LIMIT_WINDOW_SECONDS", "60").strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server_rate_limit_not_configured",
        ) from exc

    if value <= 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server_rate_limit_not_configured",
        )

    return value


def _client_ip(request: Request) -> str:
    if request.client is None or request.client.host is None:
        return "unknown"
    return request.client.host


def _endpoint(request: Request) -> str:
    return request.url.path


def _api_key_fingerprint(x_api_key: str | None) -> str:
    if x_api_key is None or not x_api_key.strip():
        return "anonymous"
    return sha256(x_api_key.encode("utf-8")).hexdigest()[:16]


def enforce_rate_limit(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> bool:
    limit = _get_limit()
    window_seconds = _get_window_seconds()

    client_ip = _client_ip(request)
    endpoint = _endpoint(request)
    key_fingerprint = _api_key_fingerprint(x_api_key)

    bucket_key = (client_ip, endpoint, key_fingerprint)
    now = time.time()
    window_start = now - window_seconds

    with _LOCK:
        bucket = _BUCKETS.setdefault(bucket_key, deque())

        while bucket and bucket[0] <= window_start:
            bucket.popleft()

        if len(bucket) >= limit:
            entry = build_request_log_entry(
                endpoint=endpoint,
                request_id=request.headers.get("x-request-id"),
                case_id=request.headers.get("x-case-id"),
                client_ip=client_ip,
                auth_status="passed",
                response_status=429,
                detail=(
                    f"rate_limited: limit={limit}, "
                    f"window_seconds={window_seconds}"
                ),
            )
            append_request_log(entry)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"rate_limit_exceeded: "
                    f"{limit} requests per {window_seconds} seconds"
                ),
            )

        bucket.append(now)

    return True
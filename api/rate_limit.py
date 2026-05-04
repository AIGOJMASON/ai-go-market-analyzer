from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Deque

from fastapi import HTTPException, Request, status

try:
    from AI_GO.api.request_logging import log_request_event
except ModuleNotFoundError:
    from api.request_logging import log_request_event


@dataclass(frozen=True)
class RateLimitDecision:
    bucket_id: str
    count: int
    limit: int
    window_seconds: int


_BUCKETS: DefaultDict[str, Deque[float]] = defaultdict(deque)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _resolve_limits() -> tuple[int, int]:
    limit = _env_int("AI_GO_RATE_LIMIT_REQUESTS", 60)
    window_seconds = _env_int("AI_GO_RATE_LIMIT_WINDOW_SECONDS", 60)

    if limit < 1:
        raise RuntimeError("AI_GO_RATE_LIMIT_REQUESTS must be >= 1")
    if window_seconds < 1:
        raise RuntimeError("AI_GO_RATE_LIMIT_WINDOW_SECONDS must be >= 1")

    return limit, window_seconds


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _bucket_id(request: Request) -> str:
    api_key_id = getattr(request.state, "operator_id", None)
    path = request.url.path

    if api_key_id:
        return f"api_key:{api_key_id}:{path}"

    client_ip = _client_ip(request)
    return f"ip:{client_ip}:{path}"


async def enforce_rate_limit(request: Request) -> RateLimitDecision:
    limit, window_seconds = _resolve_limits()

    bucket_id = _bucket_id(request)
    bucket = _BUCKETS[bucket_id]

    now = time.time()
    cutoff = now - window_seconds

    while bucket and bucket[0] <= cutoff:
        bucket.popleft()

    if len(bucket) >= limit:
        request.state.rate_limit_bucket_id = bucket_id
        request.state.rate_limit_count = len(bucket)

        log_request_event(
            event_type="rate_limit_exceeded",
            route=str(request.url.path),
            method=request.method,
            status_code=429,
            client_host=_client_ip(request),
            operator_id=getattr(request.state, "operator_id", None),
            rate_limit_bucket_id=bucket_id,
            rate_limit_count=len(bucket),
        )

        oldest = bucket[0]
        retry_after = max(1, int((oldest + window_seconds) - now))

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    bucket.append(now)

    decision = RateLimitDecision(
        bucket_id=bucket_id,
        count=len(bucket),
        limit=limit,
        window_seconds=window_seconds,
    )

    request.state.rate_limit_bucket_id = decision.bucket_id
    request.state.rate_limit_count = decision.count

    return decision
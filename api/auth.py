from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

from fastapi import Header, HTTPException, Request, status

try:
    from AI_GO.api.config import get_settings
    from AI_GO.api.request_logging import log_request_event
except ModuleNotFoundError:
    from api.config import get_settings
    from api.request_logging import log_request_event


LOCALHOST_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_key_map(raw_map: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}

    for operator_id, api_key in raw_map.items():
        clean_operator_id = str(operator_id).strip()
        clean_api_key = str(api_key).strip()

        if not clean_operator_id or not clean_api_key:
            raise ValueError("AI_GO_API_KEYS_JSON contains empty operator id or api key")

        normalized[clean_api_key] = clean_operator_id

    if not normalized:
        raise ValueError("AI_GO_API_KEYS_JSON must define at least one API key")

    return normalized


@lru_cache(maxsize=1)
def get_api_key_map() -> dict[str, str]:
    raw_keys_json = os.getenv("AI_GO_API_KEYS_JSON", "").strip()
    raw_single_key = os.getenv("AI_GO_API_KEY", "").strip()

    if raw_keys_json:
        try:
            parsed = json.loads(raw_keys_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("AI_GO_API_KEYS_JSON must be valid JSON") from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("AI_GO_API_KEYS_JSON must decode to an object")

        return _normalize_key_map(parsed)

    if raw_single_key:
        return {raw_single_key: "default_operator"}

    return {}


def clear_api_key_cache() -> None:
    get_api_key_map.cache_clear()


def _mask_api_key(raw_key: str | None) -> str | None:
    if not raw_key:
        return None
    if len(raw_key) <= 8:
        return "***"
    return f"{raw_key[:4]}...{raw_key[-4:]}"


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None


def _is_local_request(request: Request) -> bool:
    return _client_host(request) in LOCALHOST_HOSTS


def _local_dev_auth_enabled() -> bool:
    return _env_flag("AI_GO_ALLOW_LOCAL_DEV_AUTH", default=False)


def _local_dev_api_key() -> str:
    return os.getenv("AI_GO_LOCAL_DEV_API_KEY", "AIGO-local-test").strip()


def _local_dev_operator_id() -> str:
    return os.getenv("AI_GO_LOCAL_DEV_OPERATOR_ID", "local_dev_operator").strip()


def _resolve_operator_id(
    *,
    request: Request,
    incoming_key: str | None,
    key_map: dict[str, str],
) -> str | None:
    if incoming_key and incoming_key in key_map:
        return key_map[incoming_key]

    if (
        _local_dev_auth_enabled()
        and _is_local_request(request)
        and incoming_key
        and incoming_key == _local_dev_api_key()
    ):
        return _local_dev_operator_id()

    return None


async def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    key_map = get_api_key_map()
    client_host = _client_host(request)

    if x_api_key is None:
        log_request_event(
            event_type="auth_failed",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_api_key",
            api_key_header=settings.api_key_header,
            client_host=client_host,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    incoming = x_api_key.strip()
    operator_id = _resolve_operator_id(
        request=request,
        incoming_key=incoming,
        key_map=key_map,
    )

    if operator_id is None:
        log_detail = "invalid_api_key" if key_map or _local_dev_auth_enabled() else "auth_not_configured"
        detail = (
            "Invalid API key"
            if log_detail == "invalid_api_key"
            else "API key auth is not configured. Set AI_GO_API_KEYS_JSON or AI_GO_API_KEY."
        )

        log_request_event(
            event_type="auth_failed",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_detail,
            api_key_header=settings.api_key_header,
            api_key_fingerprint=_mask_api_key(x_api_key),
            client_host=client_host,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    request.state.operator_id = operator_id
    request.state.api_key_fingerprint = _mask_api_key(x_api_key)
    request.state.auth_status = "passed"

    return operator_id
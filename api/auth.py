from __future__ import annotations

import json
import os
from typing import Any

from fastapi import Header, HTTPException, Request, status

try:
    from AI_GO.api.config import get_settings
    from AI_GO.api.request_logging import log_request_event
except ModuleNotFoundError:
    from api.config import get_settings
    from api.request_logging import log_request_event


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

        key_map = _normalize_key_map(parsed)

        # DEBUG (safe, no keys exposed)
        print(f"[AUTH] Loaded {len(key_map)} API key(s)")

        return key_map

    if raw_single_key:
        print("[AUTH] Loaded single API key")
        return {raw_single_key: "default_operator"}

    raise RuntimeError("No API key configuration found.")


def _mask_api_key(raw_key: str | None) -> str | None:
    if not raw_key:
        return None
    if len(raw_key) <= 8:
        return "***"
    return f"{raw_key[:4]}...{raw_key[-4:]}"


async def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    key_map = get_api_key_map()

    if x_api_key is None:
        log_request_event(
            event_type="auth_failed",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_api_key",
            api_key_header=settings.api_key_header,
            client_host=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    incoming = x_api_key.strip()

    operator_id = key_map.get(incoming)

    if operator_id is None:
        print(f"[AUTH] Invalid key received: {incoming}")  # DEBUG

        log_request_event(
            event_type="auth_failed",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_api_key",
            api_key_header=settings.api_key_header,
            api_key_fingerprint=_mask_api_key(x_api_key),
            client_host=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    request.state.operator_id = operator_id
    request.state.api_key_fingerprint = _mask_api_key(x_api_key)

    return operator_id
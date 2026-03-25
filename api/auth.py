from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import Header, HTTPException, Request, status

from AI_GO.api.request_logging import append_request_log, build_base_log_payload


@dataclass(frozen=True)
class AuthIdentity:
    key_id: str
    operator_id: str
    label: str


def _api_key_header_name() -> str:
    value = os.getenv("AI_GO_API_KEY_HEADER", "x-api-key").strip().lower()
    return value or "x-api-key"


def _load_key_map() -> Dict[str, Dict[str, str]]:
    """
    Supported formats:

    Preferred:
    AI_GO_API_KEYS_JSON='{
      "actual-secret-key-1": {"key_id":"local","operator_id":"local_operator","label":"Local"},
      "actual-secret-key-2": {"key_id":"prod","operator_id":"render_operator","label":"Render"}
    }'

    Legacy fallback:
    AI_GO_API_KEY=single-secret
    """
    raw_json = os.getenv("AI_GO_API_KEYS_JSON", "").strip()
    single_key = os.getenv("AI_GO_API_KEY", "").strip()

    if raw_json:
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("AI_GO_API_KEYS_JSON is not valid JSON") from exc

        if not isinstance(parsed, dict) or not parsed:
            raise RuntimeError("AI_GO_API_KEYS_JSON must be a non-empty object")

        normalized: Dict[str, Dict[str, str]] = {}
        for key_value, meta in parsed.items():
            if not isinstance(key_value, str) or not key_value.strip():
                raise RuntimeError("AI_GO_API_KEYS_JSON contains an invalid key entry")

            key_value = key_value.strip()

            if isinstance(meta, str):
                operator_id = meta.strip() or "default_operator"
                normalized[key_value] = {
                    "key_id": operator_id,
                    "operator_id": operator_id,
                    "label": operator_id,
                }
                continue

            if not isinstance(meta, dict):
                raise RuntimeError("Each AI_GO_API_KEYS_JSON value must be an object or string")

            key_id = str(meta.get("key_id", "")).strip()
            operator_id = str(meta.get("operator_id", "")).strip()
            label = str(meta.get("label", "")).strip() or operator_id or key_id

            if not key_id:
                raise RuntimeError("Each AI_GO_API_KEYS_JSON entry must include key_id")
            if not operator_id:
                raise RuntimeError("Each AI_GO_API_KEYS_JSON entry must include operator_id")

            normalized[key_value] = {
                "key_id": key_id,
                "operator_id": operator_id,
                "label": label,
            }

        return normalized

    if single_key:
        return {
            single_key: {
                "key_id": "default",
                "operator_id": "default_operator",
                "label": "default",
            }
        }

    raise RuntimeError("No API key configuration found. Set AI_GO_API_KEYS_JSON or AI_GO_API_KEY.")


def _extract_presented_key(
    x_api_key: Optional[str],
    authorization: Optional[str],
) -> Optional[str]:
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()

    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer ") :].strip()
        if token:
            return token

    return None


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _log_auth_failure(request: Request, auth_status: str) -> None:
    append_request_log(
        "auth_failure",
        build_base_log_payload(
            request_id=None,
            case_id=None,
            auth_status=auth_status,
            response_status=401,
            route_mode=None,
            receipt_id=None,
            client_ip=_client_ip(request),
            api_key_id=None,
            rate_limit_bucket_id=getattr(request.state, "rate_limit_bucket_id", None),
            rate_limit_count=getattr(request.state, "rate_limit_count", None),
        ),
    )


async def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="x-api-key"),
    authorization: Optional[str] = Header(default=None),
) -> AuthIdentity:
    configured_header = _api_key_header_name()
    presented_key = _extract_presented_key(x_api_key, authorization)

    if configured_header != "x-api-key" and not presented_key:
        alt_header_value = request.headers.get(configured_header)
        if alt_header_value and alt_header_value.strip():
            presented_key = alt_header_value.strip()

    key_map = _load_key_map()

    request.state.auth_header = configured_header
    request.state.auth_present = bool(presented_key)
    request.state.client_ip = _client_ip(request)

    if not presented_key:
        request.state.auth_status = "missing"
        _log_auth_failure(request, "missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing API key. Provide header: {configured_header}",
        )

    meta = key_map.get(presented_key)
    if meta is None:
        request.state.auth_status = "invalid"
        _log_auth_failure(request, "invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    identity = AuthIdentity(
        key_id=meta["key_id"],
        operator_id=meta["operator_id"],
        label=meta["label"],
    )

    request.state.auth_status = "passed"
    request.state.api_key_id = identity.key_id
    request.state.operator_id = identity.operator_id
    request.state.operator_label = identity.label

    return identity
from __future__ import annotations

import os

from fastapi import Header, HTTPException, Request, status

from AI_GO.api.request_logging import append_request_log, build_request_log_entry


def _get_expected_api_key() -> str:
    api_key = os.getenv("AI_GO_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server_auth_not_configured",
        )
    return api_key


def _client_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _case_id(request: Request) -> str | None:
    return request.headers.get("x-case-id")


def _endpoint(request: Request) -> str:
    return request.url.path


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> bool:
    try:
        expected_api_key = _get_expected_api_key()
    except HTTPException as exc:
        entry = build_request_log_entry(
            endpoint=_endpoint(request),
            request_id=_request_id(request),
            case_id=_case_id(request),
            client_ip=_client_ip(request),
            auth_status="server_not_configured",
            response_status=500,
            detail="server_auth_not_configured",
        )
        append_request_log(entry)
        raise exc

    if x_api_key is None or x_api_key.strip() == "":
        entry = build_request_log_entry(
            endpoint=_endpoint(request),
            request_id=_request_id(request),
            case_id=_case_id(request),
            client_ip=_client_ip(request),
            auth_status="missing",
            response_status=401,
            detail="missing_api_key",
        )
        append_request_log(entry)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_api_key",
        )

    if x_api_key != expected_api_key:
        entry = build_request_log_entry(
            endpoint=_endpoint(request),
            request_id=_request_id(request),
            case_id=_case_id(request),
            client_ip=_client_ip(request),
            auth_status="invalid",
            response_status=401,
            detail="invalid_api_key",
        )
        append_request_log(entry)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_api_key",
        )

    return True
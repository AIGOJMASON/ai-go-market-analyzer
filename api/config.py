from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class ApiSettings:
    environment: str
    allowed_hosts: list[str]
    rate_limit_requests: int
    rate_limit_window_seconds: int
    api_key_header: str


def _parse_allowed_hosts(raw: str) -> list[str]:
    hosts = [host.strip() for host in raw.split(",") if host.strip()]
    if not hosts:
        raise ValueError("AI_GO_ALLOWED_HOSTS must contain at least one host")
    return hosts


def _parse_positive_int(name: str, raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer") from exc

    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")

    return value


@lru_cache(maxsize=1)
def get_settings() -> ApiSettings:
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    if not environment:
        raise ValueError("ENVIRONMENT must not be empty")

    allowed_hosts_raw = os.getenv("AI_GO_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").strip()
    rate_limit_requests_raw = os.getenv("AI_GO_RATE_LIMIT_REQUESTS", "60").strip()
    rate_limit_window_raw = os.getenv("AI_GO_RATE_LIMIT_WINDOW_SECONDS", "60").strip()
    api_key_header = os.getenv("AI_GO_API_KEY_HEADER", "x-api-key").strip()

    if not api_key_header:
        raise ValueError("AI_GO_API_KEY_HEADER must not be empty")

    return ApiSettings(
        environment=environment,
        allowed_hosts=_parse_allowed_hosts(allowed_hosts_raw),
        rate_limit_requests=_parse_positive_int("AI_GO_RATE_LIMIT_REQUESTS", rate_limit_requests_raw),
        rate_limit_window_seconds=_parse_positive_int(
            "AI_GO_RATE_LIMIT_WINDOW_SECONDS",
            rate_limit_window_raw,
        ),
        api_key_header=api_key_header,
    )


def validate_startup_settings() -> None:
    get_settings()
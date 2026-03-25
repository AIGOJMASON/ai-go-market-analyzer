from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


_ALLOWED_ENVIRONMENTS = {"development", "staging", "production"}


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    api_key_header: str
    rate_limit_requests: int
    rate_limit_window_seconds: int
    allowed_hosts: List[str]
    debug: bool


def _get_required_str(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _get_required_int(name: str) -> int:
    raw_value = _get_required_str(name)
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Invalid integer for {name}: {raw_value}") from exc

    if value <= 0:
        raise ConfigError(f"{name} must be greater than zero.")

    return value


def _parse_allowed_hosts(raw_value: str) -> List[str]:
    hosts = [item.strip() for item in raw_value.split(",") if item.strip()]
    if not hosts:
        raise ConfigError("AI_GO_ALLOWED_HOSTS must contain at least one host.")
    return hosts


def load_config() -> AppConfig:
    environment = _get_required_str("ENVIRONMENT").lower()
    if environment not in _ALLOWED_ENVIRONMENTS:
        raise ConfigError(
            "ENVIRONMENT must be one of: development, staging, production"
        )

    api_key_header = os.getenv("AI_GO_API_KEY_HEADER", "x-api-key").strip() or "x-api-key"
    rate_limit_requests = _get_required_int("AI_GO_RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds = _get_required_int(
        "AI_GO_RATE_LIMIT_WINDOW_SECONDS"
    )
    allowed_hosts = _parse_allowed_hosts(
        _get_required_str("AI_GO_ALLOWED_HOSTS")
    )

    debug = environment == "development"

    return AppConfig(
        environment=environment,
        api_key_header=api_key_header,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window_seconds=rate_limit_window_seconds,
        allowed_hosts=allowed_hosts,
        debug=debug,
    )


def validate_startup_config() -> AppConfig:
    return load_config()
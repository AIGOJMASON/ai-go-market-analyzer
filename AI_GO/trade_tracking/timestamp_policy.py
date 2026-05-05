from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_iso_timestamp(value: str) -> bool:
    try:
        normalized = value.replace("Z", "+00:00")
        datetime.fromisoformat(normalized)
        return True
    except Exception:
        return False
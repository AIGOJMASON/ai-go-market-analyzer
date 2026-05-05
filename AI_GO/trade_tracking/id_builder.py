from __future__ import annotations

import hashlib
from typing import Optional


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def build_trade_id(
    *,
    system_id: str,
    strategy_id: str,
    symbol: str,
    source_request_id: Optional[str],
    timestamp: str,
) -> str:
    seed = "|".join(
        [
            system_id,
            strategy_id,
            symbol,
            source_request_id or "",
            timestamp,
        ]
    )
    return f"trade_{_short_hash(seed)}"


def build_trade_event_id(
    *,
    event_type: str,
    trade_id: str,
    timestamp: str,
) -> str:
    compact_ts = (
        timestamp.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("T", "T")
        .replace("Z", "Z")
    )
    seed = f"{event_type}|{trade_id}|{timestamp}"
    return f"tradeevt_{compact_ts}_{_short_hash(seed)}"


def build_trade_receipt_id(*, event_id: str, timestamp: str) -> str:
    compact_ts = (
        timestamp.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("T", "T")
        .replace("Z", "Z")
    )
    seed = f"{event_id}|{timestamp}"
    return f"tradereceipt_{compact_ts}_{_short_hash(seed)}"


def build_performance_receipt_id(*, system_id: str, timestamp: str) -> str:
    compact_ts = (
        timestamp.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("T", "T")
        .replace("Z", "Z")
    )
    seed = f"{system_id}|{timestamp}"
    return f"tradeperf_{compact_ts}_{_short_hash(seed)}"
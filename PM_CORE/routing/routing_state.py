from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RoutingState:
    """
    Minimal live state for Stage 19.

    This layer is translation-only.
    It must not accumulate analytics or long-horizon memory.
    """
    last_packet_id: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)
    last_target_set: List[str] = field(default_factory=list)

    def update(self, packet_id: str, target_set: List[str]) -> None:
        self.last_packet_id = packet_id
        self.last_timestamp = utc_now_iso()
        self.last_target_set = list(target_set)
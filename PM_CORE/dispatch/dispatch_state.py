from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DispatchState:
    """
    Minimal live state for Stage 20.

    This layer is dispatch-boundary only.
    It must not accumulate analytics, memory, or orchestration state.
    """
    last_dispatch_id: str | None = None
    last_target: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, dispatch_id: str, target: str) -> None:
        self.last_dispatch_id = dispatch_id
        self.last_target = target
        self.last_timestamp = utc_now_iso()
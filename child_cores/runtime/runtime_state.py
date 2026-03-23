from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeState:
    """
    Minimal live state for Stage 22.

    This layer is runtime-boundary only.
    It must not accumulate analytics, output state, watcher state,
    continuity state, or domain history.
    """
    last_runtime_id: str | None = None
    last_target_core: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, runtime_id: str, target_core: str) -> None:
        self.last_runtime_id = runtime_id
        self.last_target_core = target_core
        self.last_timestamp = utc_now_iso()
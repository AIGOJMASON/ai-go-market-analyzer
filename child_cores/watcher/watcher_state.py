from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WatcherState:
    """
    Minimal live state for Stage 25.

    This layer is watcher-boundary only.
    It must not accumulate continuity state, publication state,
    or payload history.
    """
    last_watcher_id: str | None = None
    last_target_core: str | None = None
    last_watcher_status: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, watcher_id: str, target_core: str, watcher_status: str) -> None:
        self.last_watcher_id = watcher_id
        self.last_target_core = target_core
        self.last_watcher_status = watcher_status
        self.last_timestamp = utc_now_iso()
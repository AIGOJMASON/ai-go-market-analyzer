from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OutputState:
    """
    Minimal live state for Stage 23.

    This layer is output-boundary only.
    It must not accumulate payload history, analytics, watcher state,
    continuity state, or domain history.
    """
    last_output_id: str | None = None
    last_target_core: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, output_id: str, target_core: str) -> None:
        self.last_output_id = output_id
        self.last_target_core = target_core
        self.last_timestamp = utc_now_iso()
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ReviewState:
    """
    Minimal live state for Stage 24.

    This layer is review-boundary only.
    It must not accumulate watcher state, continuity state,
    publication state, or payload history.
    """
    last_review_id: str | None = None
    last_target_core: str | None = None
    last_disposition: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, review_id: str, target_core: str, disposition: str) -> None:
        self.last_review_id = review_id
        self.last_target_core = target_core
        self.last_disposition = disposition
        self.last_timestamp = utc_now_iso()
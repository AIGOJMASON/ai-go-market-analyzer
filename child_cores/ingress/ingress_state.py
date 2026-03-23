from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IngressState:
    """
    Minimal live state for Stage 21.

    This layer is ingress-boundary only.
    It must not accumulate analytics, memory, routing, or domain execution state.
    """
    last_ingress_id: str | None = None
    last_target_core: str | None = None
    last_timestamp: str = field(default_factory=utc_now_iso)

    def update(self, ingress_id: str, target_core: str) -> None:
        self.last_ingress_id = ingress_id
        self.last_target_core = target_core
        self.last_timestamp = utc_now_iso()
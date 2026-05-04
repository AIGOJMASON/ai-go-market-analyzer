from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderFetchResult:
    provider: str
    provider_kind: str
    fetched_at: str
    payload: dict[str, Any]
    request_context: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "provider_kind": self.provider_kind,
            "fetched_at": self.fetched_at,
            "payload": self.payload,
            "request_context": self.request_context,
        }
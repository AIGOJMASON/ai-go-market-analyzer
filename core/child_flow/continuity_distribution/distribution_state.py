from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class DistributionState:
    last_request_id: Optional[str] = None
    last_target_core: Optional[str] = None
    last_requesting_surface: Optional[str] = None
    last_consumer_profile: Optional[str] = None
    last_disposition: Optional[str] = None
    last_receipt_type: Optional[str] = None
    last_artifact_id: Optional[str] = None
    last_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "DistributionState":
        if not payload:
            return cls()
        return cls(
            last_request_id=payload.get("last_request_id"),
            last_target_core=payload.get("last_target_core"),
            last_requesting_surface=payload.get("last_requesting_surface"),
            last_consumer_profile=payload.get("last_consumer_profile"),
            last_disposition=payload.get("last_disposition"),
            last_receipt_type=payload.get("last_receipt_type"),
            last_artifact_id=payload.get("last_artifact_id"),
            last_timestamp=payload.get("last_timestamp"),
        )


def update_state(
    state: DistributionState,
    *,
    request_id: str,
    target_core: str,
    requesting_surface: str,
    consumer_profile: str,
    disposition: str,
    receipt_type: str,
    artifact_id: Optional[str],
    timestamp: str,
) -> DistributionState:
    state.last_request_id = request_id
    state.last_target_core = target_core
    state.last_requesting_surface = requesting_surface
    state.last_consumer_profile = consumer_profile
    state.last_disposition = disposition
    state.last_receipt_type = receipt_type
    state.last_artifact_id = artifact_id
    state.last_timestamp = timestamp
    return state
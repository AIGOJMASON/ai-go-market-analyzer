from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class ConsumptionState:
    last_distribution_id: Optional[str] = None
    last_requesting_surface: Optional[str] = None
    last_consumer_profile: Optional[str] = None
    last_target_core: Optional[str] = None
    last_transformation_type: Optional[str] = None
    last_disposition: Optional[str] = None
    last_receipt_type: Optional[str] = None
    last_packet_id: Optional[str] = None
    last_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "ConsumptionState":
        if not payload:
            return cls()
        return cls(
            last_distribution_id=payload.get("last_distribution_id"),
            last_requesting_surface=payload.get("last_requesting_surface"),
            last_consumer_profile=payload.get("last_consumer_profile"),
            last_target_core=payload.get("last_target_core"),
            last_transformation_type=payload.get("last_transformation_type"),
            last_disposition=payload.get("last_disposition"),
            last_receipt_type=payload.get("last_receipt_type"),
            last_packet_id=payload.get("last_packet_id"),
            last_timestamp=payload.get("last_timestamp"),
        )


def update_state(
    state: ConsumptionState,
    *,
    distribution_id: str,
    requesting_surface: str,
    consumer_profile: str,
    target_core: str,
    transformation_type: str,
    disposition: str,
    receipt_type: str,
    packet_id: Optional[str],
    timestamp: str,
) -> ConsumptionState:
    state.last_distribution_id = distribution_id
    state.last_requesting_surface = requesting_surface
    state.last_consumer_profile = consumer_profile
    state.last_target_core = target_core
    state.last_transformation_type = transformation_type
    state.last_disposition = disposition
    state.last_receipt_type = receipt_type
    state.last_packet_id = packet_id
    state.last_timestamp = timestamp
    return state
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class ContinuityState:
    last_intake_id: Optional[str] = None
    last_target_core: Optional[str] = None
    last_disposition: Optional[str] = None
    last_receipt_type: Optional[str] = None
    last_receipt_ref: Optional[str] = None
    last_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "ContinuityState":
        if not payload:
            return cls()
        return cls(
            last_intake_id=payload.get("last_intake_id"),
            last_target_core=payload.get("last_target_core"),
            last_disposition=payload.get("last_disposition"),
            last_receipt_type=payload.get("last_receipt_type"),
            last_receipt_ref=payload.get("last_receipt_ref"),
            last_timestamp=payload.get("last_timestamp"),
        )


def update_state(
    state: ContinuityState,
    *,
    intake_id: str,
    target_core: str,
    disposition: str,
    receipt_type: str,
    receipt_ref: Optional[str],
    timestamp: str,
) -> ContinuityState:
    state.last_intake_id = intake_id
    state.last_target_core = target_core
    state.last_disposition = disposition
    state.last_receipt_type = receipt_type
    state.last_receipt_ref = receipt_ref
    state.last_timestamp = timestamp
    return state
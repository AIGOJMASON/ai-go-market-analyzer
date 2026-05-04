from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LabeledOutcomeRecord:
    record_id: str
    artifact_type: str
    created_at: str

    symbol: str
    event_theme: str
    outcome_class: str
    directional_bias: str

    observed_at: str
    source_type: str

    return_pct: Optional[float] = None
    hold_duration_bars: Optional[int] = None
    setup_type: Optional[str] = None
    headline: Optional[str] = None
    sector: Optional[str] = None
    source_request_id: Optional[str] = None
    source_closeout_id: Optional[str] = None
    notes: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
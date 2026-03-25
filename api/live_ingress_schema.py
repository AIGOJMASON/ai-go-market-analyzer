from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LiveIngressRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    headline: str = Field(..., min_length=1)
    price_change_pct: float
    sector: str = Field(..., min_length=1)
    confirmation: str = Field(..., min_length=1)


class HistoricalAnalogPanel(BaseModel):
    artifact_type: str
    artifact_class: str
    sealed: bool
    event_theme: str
    analog_count: int
    common_pattern: str
    failure_mode: str
    confidence_band: str
    matched_signal_count: int
    analogs: List[Dict[str, Any]]
    notes: str
    source_lineage: Dict[str, Any]


class LiveIngressPacket(BaseModel):
    artifact_type: str
    sealed: bool
    request_id: str
    symbol: str
    headline: str
    sector: str
    confirmation: str
    price_change_pct: float
    event_theme: str
    classification_panel: Dict[str, Any]
    signal_stack_panel: Dict[str, Any]
    historical_analog_panel: HistoricalAnalogPanel
    market_panel: Dict[str, Any]
    candidate_panel: Dict[str, Any]
    governance_panel: Dict[str, Any]
    refinement_packet: Dict[str, Any]
    notes: Optional[str] = None
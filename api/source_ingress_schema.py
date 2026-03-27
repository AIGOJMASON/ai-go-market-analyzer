from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator


ApprovedSourceType = Literal[
    "operator_manual",
    "newswire",
    "rss_feed",
    "watchlist_note",
    "macro_note",
    "social_observation",
]

ApprovedSector = Literal[
    "energy",
    "materials",
    "industrials",
    "utilities",
    "financials",
    "technology",
    "healthcare",
    "consumer_staples",
    "consumer_discretionary",
    "real_estate",
    "communication_services",
    "unknown",
]

ApprovedConfirmation = Literal[
    "confirmed",
    "partial",
    "missing",
    "unknown",
]


class SourceIngressRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=128)
    source_item_id: str = Field(min_length=1, max_length=128)
    source_type: ApprovedSourceType
    headline: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", max_length=2000)
    symbol_hint: Optional[str] = Field(default=None, max_length=16)
    sector_hint: ApprovedSector = "unknown"
    confirmation_hint: ApprovedConfirmation = "unknown"
    price_change_pct: Optional[float] = None
    occurred_at: Optional[str] = None
    source_name: Optional[str] = Field(default=None, max_length=128)
    source_url: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list, max_length=12)

    @field_validator("symbol_hint")
    @classmethod
    def normalize_symbol(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().upper()
        if not normalized:
            return None
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: List[str]) -> List[str]:
        normalized: List[str] = []
        for item in values:
            cleaned = item.strip().lower()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized


class SourceAnalyzeCandidateRequest(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=256)
    request_id: Optional[str] = Field(default=None, max_length=128)


class SourceSignalRecord(BaseModel):
    artifact_type: Literal["source_signal_record"] = "source_signal_record"
    sealed: bool = True
    request_id: str
    source_item_id: str
    source_type: ApprovedSourceType
    trust_class: str
    headline: str
    body: str
    normalized_symbol: Optional[str] = None
    normalized_sector: ApprovedSector = "unknown"
    normalized_confirmation: ApprovedConfirmation = "unknown"
    event_theme: str
    propagation: str
    price_change_pct: Optional[float] = None
    severity: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    occurred_at: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    suggestion_status: Literal["new", "clustered", "dismissed", "promoted"] = "new"
    execution_influence: bool = False
    recommendation_mutation_allowed: bool = False
    runtime_mutation_allowed: bool = False
    provenance_required: bool = True


class SourceClusterMember(BaseModel):
    source_item_id: str
    headline: str
    source_type: ApprovedSourceType
    severity: str
    event_theme: str
    normalized_symbol: Optional[str] = None
    normalized_sector: ApprovedSector = "unknown"


class SourceClusterRecord(BaseModel):
    artifact_type: Literal["source_cluster_record"] = "source_cluster_record"
    sealed: bool = True
    cluster_key: str
    event_theme: str
    normalized_symbol: Optional[str] = None
    normalized_sector: ApprovedSector = "unknown"
    source_count: int
    suggestion_strength: str
    members: List[SourceClusterMember]
    execution_influence: bool = False
    recommendation_mutation_allowed: bool = False
    runtime_mutation_allowed: bool = False


class SourceCandidateRecord(BaseModel):
    artifact_type: Literal["source_candidate_record"] = "source_candidate_record"
    sealed: bool = True
    candidate_id: str
    cluster_key: str
    symbol: Optional[str] = None
    sector: ApprovedSector = "unknown"
    event_theme: str
    source_count: int
    suggestion_class: Literal["monitor", "review", "analyze", "dismiss"]
    suggestion_reason: str
    confirmation_state: ApprovedConfirmation
    propagation: str
    execution_influence: bool = False
    recommendation_mutation_allowed: bool = False
    runtime_mutation_allowed: bool = False


class SourceInboxRecord(BaseModel):
    artifact_type: Literal["source_inbox_record"] = "source_inbox_record"
    sealed: bool = True
    incoming_signals: List[SourceSignalRecord]
    candidate_cases: List[SourceCandidateRecord]
    summary: dict
    execution_influence: bool = False
    recommendation_mutation_allowed: bool = False
    runtime_mutation_allowed: bool = False

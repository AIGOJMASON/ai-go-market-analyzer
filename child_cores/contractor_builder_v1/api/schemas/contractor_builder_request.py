from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


ProjectType = Literal["remodel", "repair", "new_build", "maintenance"]
TradeFocus = Literal["general", "roofing", "electrical", "plumbing", "hvac", "interior", "exterior"]
BudgetBand = Literal["low", "medium", "high"]
TimelineBand = Literal["urgent", "near_term", "flexible"]
LocationMode = Literal["onsite", "remote", "hybrid"]


class ContractorBuilderLiveRequest(BaseModel):
    request_id: str
    project_type: ProjectType
    trade_focus: TradeFocus
    scope_summary: str
    budget_band: BudgetBand
    timeline_band: TimelineBand
    location_mode: LocationMode
    confirmation: Literal["confirmed", "partial", "missing"] = "partial"
    force_rejection: bool = False


class ContractorBuilderFixtureRequest(BaseModel):
    request_id: str
    case_id: Optional[str] = None
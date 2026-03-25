from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ReviewDecisionRequest(BaseModel):
    closeout_id: str = Field(..., min_length=1)
    reviewer_id: str = Field(..., min_length=1)
    decision: str = Field(..., min_length=1)
    notes: Optional[str] = Field(default=None, max_length=2000)
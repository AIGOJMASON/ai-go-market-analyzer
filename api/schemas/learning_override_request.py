from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LearningOverrideRequest(BaseModel):
    candidate_id: str = Field(..., min_length=1)
    reviewer_id: str = Field(..., min_length=1)
    override_reason: str = Field(..., min_length=1, max_length=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MarketAnalyzerRequest(BaseModel):
    request_id: Optional[str] = Field(
        default=None,
        description="Optional caller-supplied request identifier.",
    )
    case_id: Optional[str] = Field(
        default=None,
        description="Optional live-style case identifier. Defaults to the core's default case when omitted.",
    )
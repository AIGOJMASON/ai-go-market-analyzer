from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ChecklistItem(BaseModel):
    item_id: str
    phase_id: str
    label: str
    required: bool = True
    status: str = "not_started"
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class PhaseChecklist(BaseModel):
    project_id: str
    phase_id: str
    items: List[ChecklistItem]
    required_item_count: int
    completed_required_count: int
    ready_for_signoff: bool
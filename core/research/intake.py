from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class IntakeRecord:
    intake_id: str
    timestamp: str
    signal_type: str
    title: str
    summary: str
    source_material: List[Dict[str, Any]]
    source_metadata: Dict[str, Any]
    intake_context: Dict[str, Any]
    status: str


class ResearchIntakeService:
    """
    Normalizes raw external signal into a governed intake record.
    """

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def create_intake_record(
        self,
        signal_type: str,
        title: str,
        summary: str,
        source_material: Optional[List[Dict[str, Any]]] = None,
        source_metadata: Optional[Dict[str, Any]] = None,
        intake_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = IntakeRecord(
            intake_id=f"AI-GO-INTAKE-{uuid4().hex[:12].upper()}",
            timestamp=self._timestamp(),
            signal_type=signal_type,
            title=title,
            summary=summary,
            source_material=source_material or [],
            source_metadata=source_metadata or {},
            intake_context=intake_context or {},
            status="intake_normalized",
        )
        return asdict(record)
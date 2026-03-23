from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class ResearchScreeningService:
    """
    Screens intake records and source material for basic structural validity
    and downstream readiness.
    """

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def screen_intake_record(self, intake_record: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []

        if not intake_record.get("title"):
            issues.append("missing title")

        if not intake_record.get("summary"):
            issues.append("missing summary")

        if not isinstance(intake_record.get("source_material", []), list):
            issues.append("source_material must be a list")

        passed = len(issues) == 0

        return {
            "screening_id": f"AI-GO-SCREEN-{int(self._timestamp().replace('-', '').replace(':', '').replace('+00:00', '').replace('T', ''))}",
            "timestamp": self._timestamp(),
            "intake_id": intake_record.get("intake_id"),
            "status": "screened",
            "passed": passed,
            "issues": issues,
            "screened_record": intake_record,
        }
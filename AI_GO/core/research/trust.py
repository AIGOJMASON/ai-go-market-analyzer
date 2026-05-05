from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class ResearchTrustService:
    """
    Assigns trust classification and confidence surfaces to screened research input.
    """

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def classify_trust(self, screening_result: Dict[str, Any]) -> Dict[str, Any]:
        issues = screening_result.get("issues", [])
        passed = screening_result.get("passed", False)

        if passed and not issues:
            trust_class = "screened"
            confidence = 0.85
        elif passed:
            trust_class = "provisional"
            confidence = 0.65
        else:
            trust_class = "low_confidence"
            confidence = 0.30

        return {
            "trust_id": f"AI-GO-TRUST-{int(self._timestamp().replace('-', '').replace(':', '').replace('+00:00', '').replace('T', ''))}",
            "timestamp": self._timestamp(),
            "intake_id": screening_result.get("intake_id"),
            "screening_id": screening_result.get("screening_id"),
            "trust_class": trust_class,
            "confidence": confidence,
            "status": "trust_classified",
        }
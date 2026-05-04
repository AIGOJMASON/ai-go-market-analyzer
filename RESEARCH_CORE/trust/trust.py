"""
RESEARCH_CORE.trust.trust

Explicit trust classification service for screened research inputs.
This module assigns a declared trust class after screening and before packet emission.
"""

from __future__ import annotations

from typing import Any, Dict

from .trust_model import classify_trust


def assign_trust_class(screening_result: Dict[str, Any], intake_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign a trust classification to a screened intake record.

    Trust assignment occurs only after screening.
    This module does not emit packets or perform PM interpretation.
    """
    screening_status = screening_result.get("screening_status")
    trust_result = classify_trust(screening_status=screening_status, intake_record=intake_record)

    return {
        "trust_class": trust_result["trust_class"],
        "trust_rationale": trust_result["trust_rationale"],
        "trust_inputs": trust_result["trust_inputs"],
    }
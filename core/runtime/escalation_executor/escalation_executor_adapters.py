from __future__ import annotations

from typing import Any, Dict


def operator_queue_escalation_adapter(decision: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Escalation executed through operator queue escalation adapter.",
        "result": "escalated",
        "escalation_attempted": True,
    }


def retry_governance_escalation_adapter(decision: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Escalation executed through retry governance escalation adapter.",
        "result": "escalated",
        "escalation_attempted": True,
    }
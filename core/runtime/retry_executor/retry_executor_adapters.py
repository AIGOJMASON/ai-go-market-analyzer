from __future__ import annotations

from typing import Any, Dict


def manual_retry_adapter(decision: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Retry executed through manual retry adapter.",
        "result": "retried",
        "retry_attempted": True,
    }


def gated_auto_retry_adapter(decision: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Retry executed through gated auto retry adapter.",
        "result": "retried",
        "retry_attempted": True,
    }
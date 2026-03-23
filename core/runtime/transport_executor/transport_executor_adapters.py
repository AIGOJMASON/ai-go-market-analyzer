from __future__ import annotations

from typing import Any, Dict


def manual_release_adapter(envelope: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Transport envelope executed through manual release adapter.",
        "result": "executed",
        "execution_attempted": True,
    }


def gated_auto_release_adapter(envelope: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "Transport envelope executed through gated auto release adapter.",
        "result": "executed",
        "execution_attempted": True,
    }
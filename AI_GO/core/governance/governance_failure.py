from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def raise_governance_failure(
    *,
    status_code: int = 409,
    error: str,
    message: str,
    context: Dict[str, Any],
) -> None:
    context = _safe_dict(context)

    raise HTTPException(
        status_code=status_code,
        detail={
            "error": error,
            "message": message,
            "state": _safe_dict(context.get("state")),
            "watcher": _safe_dict(context.get("watcher")),
            "governance_decision": _safe_dict(context.get("governance_decision")),
        },
    )
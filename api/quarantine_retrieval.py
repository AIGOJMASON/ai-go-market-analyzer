from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.state_runtime.state_paths import receipts_root


class QuarantineRetrievalError(ValueError):
    pass


def _quarantine_root() -> Path:
    return receipts_root() / "market_analyzer_v1" / "quarantine"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise QuarantineRetrievalError(f"quarantine artifact not found: {path.name}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QuarantineRetrievalError(f"invalid quarantine json: {path.name}") from exc

    if not isinstance(payload, dict):
        raise QuarantineRetrievalError(f"quarantine artifact must be a dict: {path.name}")

    return payload


def get_quarantine_closeout(closeout_id: str) -> Dict[str, Any]:
    clean_id = str(closeout_id or "").strip()
    if not clean_id:
        raise QuarantineRetrievalError("closeout_id is required")

    return _read_json(_quarantine_root() / f"{clean_id}.json")


def list_quarantine_closeouts(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise QuarantineRetrievalError("limit must be >= 1")
    if offset < 0:
        raise QuarantineRetrievalError("offset must be >= 0")

    root = _quarantine_root()
    items: List[Dict[str, Any]] = []

    if root.exists():
        for path in sorted(root.glob("*.json"), reverse=True):
            try:
                payload = _read_json(path)
            except QuarantineRetrievalError:
                continue
            items.append(_safe_dict(payload))

    paged = items[offset: offset + limit]

    return {
        "artifact_type": "market_analyzer_quarantine_index",
        "sealed": True,
        "count": len(paged),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged,
    }
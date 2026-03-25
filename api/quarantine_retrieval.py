from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


QUARANTINE_ROOT = Path("AI_GO/receipts/market_analyzer_v1/quarantine")


class QuarantineRetrievalError(ValueError):
    pass


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _iter_quarantine_paths() -> List[Path]:
    if not QUARANTINE_ROOT.exists():
        return []
    return sorted(QUARANTINE_ROOT.glob("*.json"), reverse=True)


def _load_quarantine_artifact(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QuarantineRetrievalError(f"invalid quarantine artifact: {path.name}") from exc

    if not isinstance(payload, dict):
        raise QuarantineRetrievalError(f"invalid quarantine payload type: {path.name}")

    return payload


def _normalize_quarantine_item(closeout: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "closeout_id": closeout.get("closeout_id"),
        "route_mode": closeout.get("route_mode"),
        "closeout_status": closeout.get("closeout_status"),
        "requires_review": closeout.get("requires_review", True),
        "closeout_artifact": _safe_dict(closeout),
    }


def list_quarantined_closeouts(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise QuarantineRetrievalError("limit must be >= 1")
    if offset < 0:
        raise QuarantineRetrievalError("offset must be >= 0")

    items: List[Dict[str, Any]] = []
    for path in _iter_quarantine_paths():
        try:
            closeout = _load_quarantine_artifact(path)
        except QuarantineRetrievalError:
            continue
        items.append(_normalize_quarantine_item(closeout))

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "quarantine_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }


def get_quarantine_closeout(closeout_id: str) -> Dict[str, Any]:
    closeout_id = str(closeout_id or "").strip()
    if not closeout_id:
        raise QuarantineRetrievalError("closeout_id is required")

    path = QUARANTINE_ROOT / f"{closeout_id}.json"
    if not path.exists():
        raise QuarantineRetrievalError(f"quarantine closeout not found: {closeout_id}")

    closeout = _load_quarantine_artifact(path)
    return _normalize_quarantine_item(closeout)
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


BASE_PATH = Path("AI_GO/receipts/market_analyzer_v1")

RECEIPT_ROOT = BASE_PATH / "receipts"
VALIDATION_ROOT = BASE_PATH / "watcher"
CLOSEOUT_ROOT = BASE_PATH / "closeout"


class ArtifactRetrievalError(ValueError):
    pass


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactRetrievalError(f"artifact_not_found:{path.name}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactRetrievalError(f"invalid_json:{path.name}") from exc


def get_receipt_by_id(receipt_id: str) -> Dict[str, Any]:
    receipt_id = str(receipt_id or "").strip()
    if not receipt_id:
        raise ArtifactRetrievalError("receipt_id is required")

    path = RECEIPT_ROOT / f"{receipt_id}.json"
    return _load_json(path)


def get_validation_by_id(validation_id: str) -> Dict[str, Any]:
    validation_id = str(validation_id or "").strip()
    if not validation_id:
        raise ArtifactRetrievalError("validation_id is required")

    path = VALIDATION_ROOT / f"{validation_id}.json"
    return _load_json(path)


def get_closeout_by_id(closeout_id: str) -> Dict[str, Any]:
    closeout_id = str(closeout_id or "").strip()
    if not closeout_id:
        raise ArtifactRetrievalError("closeout_id is required")

    path = CLOSEOUT_ROOT / f"{closeout_id}.json"
    return _load_json(path)
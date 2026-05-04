from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _resolve_project_root() -> Path:
    current = Path(__file__).resolve()

    for candidate in [current] + list(current.parents):
        if (candidate / "AI_GO").exists() and (candidate / "AI_GO" / "receipts").exists():
            return candidate / "AI_GO"

        if (candidate / "receipts").exists() and (candidate / "api").exists():
            return candidate

    return current.parents[1]


PROJECT_ROOT = _resolve_project_root()

BASE_PATH = PROJECT_ROOT / "receipts" / "market_analyzer_v1"
RECEIPT_ROOT = BASE_PATH / "receipts"
VALIDATION_ROOT = BASE_PATH / "watcher"
CLOSEOUT_ROOT = BASE_PATH / "closeout"


class ArtifactRetrievalError(ValueError):
    pass


def _clean_required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ArtifactRetrievalError(f"{field_name} is required")
    return cleaned


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactRetrievalError(f"artifact_not_found:{path.name}")

    if not path.is_file():
        raise ArtifactRetrievalError(f"artifact_path_not_file:{path.name}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactRetrievalError(f"invalid_json:{path.name}") from exc

    if not isinstance(payload, dict):
        raise ArtifactRetrievalError(f"artifact_not_object:{path.name}")

    return payload


def get_receipt_by_id(receipt_id: str) -> Dict[str, Any]:
    clean_receipt_id = _clean_required(receipt_id, "receipt_id")
    return _load_json(RECEIPT_ROOT / f"{clean_receipt_id}.json")


def get_validation_by_id(validation_id: str) -> Dict[str, Any]:
    clean_validation_id = _clean_required(validation_id, "validation_id")
    return _load_json(VALIDATION_ROOT / f"{clean_validation_id}.json")


def get_closeout_by_id(closeout_id: str) -> Dict[str, Any]:
    clean_closeout_id = _clean_required(closeout_id, "closeout_id")
    return _load_json(CLOSEOUT_ROOT / f"{clean_closeout_id}.json")
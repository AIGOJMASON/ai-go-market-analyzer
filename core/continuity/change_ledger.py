from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_change_ledger_path() -> Path:
    return get_project_root() / "state" / "smi" / "current" / "change_ledger.json"


def _default_ledger() -> Dict[str, Any]:
    return {
        "status": "active",
        "last_updated": None,
        "changes": [],
    }


def load_change_ledger() -> Dict[str, Any]:
    path = get_change_ledger_path()

    if not path.exists():
        return _default_ledger()

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Change ledger must decode to a dict")

    payload.setdefault("status", "active")
    payload.setdefault("last_updated", None)
    payload.setdefault("changes", [])

    if not isinstance(payload["changes"], list):
        raise ValueError("Change ledger changes field must be a list")

    return payload


def save_change_ledger(ledger: Dict[str, Any]) -> str:
    path = get_change_ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(ledger, handle, indent=2, ensure_ascii=False)

    return str(path)


def record_change(change: Dict[str, Any]) -> Dict[str, Any]:
    ledger = load_change_ledger()
    changes = list(ledger.get("changes", []))
    changes.append(change)

    ledger["changes"] = changes
    ledger["last_updated"] = change.get("recorded_at")

    ledger_path = save_change_ledger(ledger)

    return {
        "status": "recorded",
        "ledger_path": ledger_path,
        "change_index": len(changes) - 1,
        "change": change,
    }
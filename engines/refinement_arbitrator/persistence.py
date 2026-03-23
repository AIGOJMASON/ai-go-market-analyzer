from __future__ import annotations

import json
import os
from typing import Any, Dict, Mapping


def _repo_root() -> str:
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def refinement_state_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "state", "refinement_arbitrator", "current"))


def refinement_receipts_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "state", "refinement_arbitrator", "receipts"))


def pm_receipts_dir() -> str:
    return _ensure_dir(os.path.join(_repo_root(), "PM_CORE", "state", "receipts"))


def persist_json(path: str, payload: Mapping[str, Any]) -> str:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return path


def persist_arbitration_decision(decision: Mapping[str, Any]) -> str:
    arbitration_id = str(decision["arbitration_id"])
    filename = f"{arbitration_id}__decision.json"
    path = os.path.join(refinement_state_dir(), filename)
    return persist_json(path, decision)


def persist_arbitration_receipt(receipt: Mapping[str, Any]) -> str:
    arbitration_id = str(receipt["arbitration_id"])
    filename = f"{arbitration_id}__receipt.json"
    path = os.path.join(refinement_receipts_dir(), filename)
    return persist_json(path, receipt)


def persist_pm_intake_receipt(receipt: Mapping[str, Any]) -> str:
    pm_intake_id = str(receipt["pm_intake_id"])
    filename = f"{pm_intake_id}__pm_intake_receipt.json"
    path = os.path.join(pm_receipts_dir(), filename)
    return persist_json(path, receipt)
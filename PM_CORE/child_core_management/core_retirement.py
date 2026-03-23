from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .child_core_registry import PM_CORE_DIR, get_entry, retire_core, update_core_entry


RECEIPTS_DIR = PM_CORE_DIR / "state" / "receipts"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _retirement_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__retirement_receipt.json"


def retire_child_core(core_id: str, *, reason: str, operator: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    if entry.get("status") == "retired":
        raise ValueError(f"Child core '{core_id}' is already retired.")

    retired_at = _utc_now()
    receipt = {
        "status": "child_core_retired",
        "core_id": core_id,
        "reason": reason,
        "operator": operator,
        "notes": notes,
        "retired_at": retired_at,
        "prior_status": entry.get("status"),
        "core_path": entry.get("core_path"),
        "activation_receipt_path": entry.get("activation_receipt_path"),
    }
    receipt_path = _retirement_receipt_path(core_id)
    _write_json(receipt_path, receipt)

    updated = retire_core(
        core_id,
        receipt_path.as_posix(),
        notes=notes or reason,
    )
    update_core_entry(core_id, {"updated_at": retired_at})

    return {
        "status": "retired",
        "core_id": core_id,
        "retirement_receipt_path": receipt_path.as_posix(),
        "registry_entry": updated,
    }
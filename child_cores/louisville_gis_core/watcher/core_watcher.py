from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "louisville_gis_core"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_core_root() -> Path:
    return get_project_root() / "child_cores" / CORE_ID


def get_watcher_dir() -> Path:
    return get_core_root() / "watcher"


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return str(path)


def _legacy_block_receipt_path() -> Path:
    return get_watcher_dir() / "legacy_watcher_block_receipt.json"


def verify_louisville_gis_execution(
    *,
    inheritance_state_path: str,
    execution_record_path: str,
    output_path: str,
) -> Dict[str, Any]:
    """
    Legacy surface retired for Stage 23 compliance.

    Watcher verification may not be invoked from legacy child-core execution
    flow. Monitoring must be introduced only by a later governed stage.
    """
    receipt = {
        "status": "blocked",
        "core_id": CORE_ID,
        "recorded_at": _utc_now_iso(),
        "reason": "watcher_invocation_not_lawful_before_governed_monitoring_stage",
        "received_paths": {
            "inheritance_state_path": inheritance_state_path,
            "execution_record_path": execution_record_path,
            "output_path": output_path,
        },
        "allowed_future_boundary": "stage24_monitoring",
    }
    receipt_path = _write_json(_legacy_block_receipt_path(), receipt)

    return {
        "status": "blocked",
        "watcher_receipt_path": receipt_path,
        "reason": receipt["reason"],
    }
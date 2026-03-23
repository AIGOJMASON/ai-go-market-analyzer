from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CORE_ID = "contractor_proposals_core"
CORE_ROOT = Path(__file__).resolve().parents[1]
WATCHER_DIR = CORE_ROOT / "watcher"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _legacy_block_receipt_path() -> Path:
    return WATCHER_DIR / "legacy_watcher_block_receipt.json"


def verify_child_core_artifacts(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy surface retired for Stage 23 compliance.

    Watcher verification may not be invoked from legacy child-core execution
    flow. Monitoring must be introduced only by a later governed stage.
    """
    receipt = {
        "status": "blocked",
        "packet_id": artifacts.get("packet_id"),
        "core_id": CORE_ID,
        "verified_at": _utc_now(),
        "reason": "watcher_invocation_not_lawful_before_governed_monitoring_stage",
        "received_artifacts": artifacts,
        "allowed_future_boundary": "stage24_monitoring",
    }

    receipt_path = _legacy_block_receipt_path()
    _write_json(receipt_path, receipt)

    return {
        "status": "blocked",
        "watcher_receipt_path": receipt_path.as_posix(),
        "reason": receipt["reason"],
    }
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4


CLOSEOUT_OUTPUT_DIR = Path("AI_GO/receipts/market_analyzer_v1/closeout")
QUARANTINE_OUTPUT_DIR = Path("AI_GO/receipts/market_analyzer_v1/quarantine")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_closeout_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid4().hex[:10]
    return f"closeout_market_analyzer_v1_{timestamp}_{nonce}"


def build_closeout_result(
    *,
    receipt: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> Dict[str, Any]:
    passed = bool(validation_result.get("passed"))
    closeout_status = "accepted" if passed else "quarantined"

    return {
        "closeout_id": _generate_closeout_id(),
        "artifact_type": "market_analyzer_closeout",
        "artifact_version": "v1",
        "closed_at": _utc_now_iso(),
        "core_id": receipt.get("core_id"),
        "receipt_id": receipt.get("receipt_id"),
        "watcher_validation_id": validation_result.get("validation_id"),
        "watcher_status": validation_result.get("watcher_status"),
        "closeout_status": closeout_status,
        "accepted": passed,
        "requires_review": not passed,
        "issues": validation_result.get("issues", []),
        "policy": {
            "on_pass": "accepted",
            "on_fail": "quarantined",
            "execution_allowed": False,
            "approval_required": True,
        },
        "lineage": {
            "source_receipt_id": receipt.get("receipt_id"),
            "source_validation_id": validation_result.get("validation_id"),
            "source_artifact_type": receipt.get("artifact_type"),
            "validation_artifact_type": validation_result.get("artifact_type"),
        },
    }


def persist_closeout_result(closeout_result: Dict[str, Any]) -> Path:
    closeout_status = closeout_result.get("closeout_status")

    # Always persist to closeout archive
    CLOSEOUT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    closeout_id = closeout_result["closeout_id"]

    closeout_path = CLOSEOUT_OUTPUT_DIR / f"{closeout_id}.json"
    with closeout_path.open("w", encoding="utf-8") as handle:
        json.dump(closeout_result, handle, ensure_ascii=False, indent=2)

    # 🔥 NEW: If quarantined → ALSO persist to quarantine index
    if closeout_status == "quarantined":
        QUARANTINE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        quarantine_path = QUARANTINE_OUTPUT_DIR / f"{closeout_id}.json"
        with quarantine_path.open("w", encoding="utf-8") as handle:
            json.dump(closeout_result, handle, ensure_ascii=False, indent=2)

    return closeout_path
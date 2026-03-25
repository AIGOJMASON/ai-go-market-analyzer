import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4


WATCHER_OUTPUT_DIR = Path("AI_GO/receipts/market_analyzer_v1/watcher")
VALID_AUTH_STATUSES = {"passed", "missing", "invalid"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_validation_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid4().hex[:10]
    return f"watcher_market_analyzer_v1_{timestamp}_{nonce}"


def validate_market_analyzer_receipt(receipt: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[str] = []

    if not receipt.get("receipt_id"):
        issues.append("missing receipt_id")

    if receipt.get("artifact_type") != "market_analyzer_run_receipt":
        issues.append("invalid artifact_type")

    if receipt.get("artifact_version") != "v1":
        issues.append("invalid artifact_version")

    if receipt.get("core_id") != "market_analyzer_v1":
        issues.append("invalid core_id")

    if not receipt.get("route_mode"):
        issues.append("missing route_mode")

    governance = receipt.get("governance", {})
    if governance.get("mode") != "advisory":
        issues.append("invalid governance.mode")
    if governance.get("execution_allowed") is not False:
        issues.append("governance.execution_allowed must be false")
    if governance.get("approval_required") is not True:
        issues.append("governance.approval_required must be true")

    auth_context = receipt.get("auth_context", {})
    auth_status = auth_context.get("auth_status")
    if auth_status not in VALID_AUTH_STATUSES:
        issues.append("invalid auth_context.auth_status")

    if auth_status != "passed":
        issues.append("auth_context.auth_status must be passed for accepted live execution")

    if not auth_context.get("api_key_id"):
        issues.append("missing auth_context.api_key_id")

    if not auth_context.get("client_ip"):
        issues.append("missing auth_context.client_ip")

    lineage = receipt.get("lineage", {})
    if lineage.get("watcher_ready") is not True:
        issues.append("lineage.watcher_ready must be true")

    passed = len(issues) == 0
    watcher_status = "passed" if passed else "failed"

    return {
        "validation_id": _generate_validation_id(),
        "artifact_type": "market_analyzer_receipt_validation",
        "artifact_version": "v1",
        "validator": "market_analyzer_receipt_watcher_v1",
        "validated_at": _utc_now_iso(),
        "receipt_id": receipt.get("receipt_id"),
        "core_id": receipt.get("core_id"),
        "watcher_status": watcher_status,
        "passed": passed,
        "issues": issues,
        "lineage": {
            "source_receipt_id": receipt.get("receipt_id"),
            "source_artifact_type": receipt.get("artifact_type"),
            "validation_target": "market_analyzer_run_receipt",
        },
    }


def persist_validation_result(validation_result: Dict[str, Any]) -> Path:
    WATCHER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    validation_id = validation_result["validation_id"]
    path = WATCHER_OUTPUT_DIR / f"{validation_id}.json"

    with path.open("w", encoding="utf-8") as handle:
        json.dump(validation_result, handle, ensure_ascii=False, indent=2)

    return path
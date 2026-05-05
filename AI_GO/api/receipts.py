from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Request

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import receipts_root


RECEIPT_MUTATION_CLASS = "market_analyzer_receipt_persistence"
RECEIPT_PERSISTENCE_TYPE = "market_analyzer_receipt"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_recommendation": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "authority_scope": "market_analyzer_receipt_artifact",
}


def _receipts_dir() -> Path:
    return receipts_root() / "market_analyzer_v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _build_receipt_id() -> str:
    ts = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    return f"market_analyzer_run_{ts}_{uuid4().hex[:10]}"


def _client_ip(request: Optional[Request]) -> str:
    if request is None or request.client is None:
        return "unknown"
    return str(request.client.host or "unknown")


def _api_key_id(request: Optional[Request]) -> str:
    if request is None:
        return "unknown"
    return str(
        getattr(request.state, "api_key_fingerprint", "")
        or getattr(request.state, "operator_id", "")
        or "unknown"
    )


def _auth_status(request: Optional[Request]) -> str:
    if request is None:
        return "unknown"
    return str(getattr(request.state, "auth_status", "") or "passed")


def _normalize_receipt(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "market_analyzer_run_receipt")
    normalized.setdefault("artifact_version", "v1")
    normalized["persistence_type"] = RECEIPT_PERSISTENCE_TYPE
    normalized["mutation_class"] = RECEIPT_MUTATION_CLASS
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_receipt(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": RECEIPT_PERSISTENCE_TYPE,
        "mutation_class": RECEIPT_MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def build_run_receipt(
    *,
    request_id: Optional[str] = None,
    core_id: str = "market_analyzer_v1",
    route_mode: str = "pm_route",
    request: Optional[Request] = None,
    response_payload: Optional[Dict[str, Any]] = None,
    watcher_ready: bool = True,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = response_payload if isinstance(response_payload, dict) else {}

    receipt = {
        "receipt_id": _build_receipt_id(),
        "artifact_type": "market_analyzer_run_receipt",
        "artifact_version": "v1",
        "created_at": _utc_now_iso(),
        "request_id": request_id or payload.get("request_id"),
        "core_id": core_id,
        "route_mode": route_mode,
        "governance": {
            "mode": "advisory",
            "execution_allowed": False,
            "approval_required": True,
        },
        "auth_context": {
            "auth_status": _auth_status(request),
            "api_key_id": _api_key_id(request),
            "client_ip": _client_ip(request),
        },
        "lineage": {
            "watcher_ready": bool(watcher_ready),
            "source": "AI_GO.api.receipts",
        },
        "summary": {
            "status": payload.get("status"),
            "recommendation_count": (
                payload.get("recommendation_panel", {}).get("count")
                if isinstance(payload.get("recommendation_panel"), dict)
                else None
            ),
        },
    }

    if extra:
        receipt["extra"] = dict(extra)

    return _normalize_receipt(receipt)


def persist_receipt(receipt: Dict[str, Any]) -> Path:
    receipt_id = str(receipt.get("receipt_id", "")).strip()
    if not receipt_id:
        raise ValueError("receipt_id is required")

    directory = _receipts_dir() / "receipts"
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{receipt_id}.json"
    _governed_write(path, receipt)
    return path


def load_receipt(receipt_id: str) -> Dict[str, Any]:
    clean_id = str(receipt_id or "").strip()
    if not clean_id:
        raise ValueError("receipt_id is required")

    path = _receipts_dir() / "receipts" / f"{clean_id}.json"
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}
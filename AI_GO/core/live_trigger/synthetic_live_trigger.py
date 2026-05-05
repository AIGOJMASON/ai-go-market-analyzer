from __future__ import annotations

import inspect
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from AI_GO.core.governance.governed_persistence import governed_write_json


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "state" / "live_trigger"
CURRENT_DIR = STATE_DIR / "current"
RECEIPTS_DIR = STATE_DIR / "receipts"

STATE_PATH = CURRENT_DIR / "live_trigger_state.json"
LATEST_RESPONSE_PATH = CURRENT_DIR / "latest_live_trigger_response.json"

DEFAULT_URL = "http://127.0.0.1:8000/market-analyzer/run/live"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_API_KEY_HEADER = "x-api-key"

MUTATION_CLASS = "awareness_persistence"
RECEIPT_MUTATION_CLASS = "receipt"
PERSISTENCE_TYPE_STATE = "live_trigger_state"
PERSISTENCE_TYPE_RESPONSE = "live_trigger_response_snapshot"
PERSISTENCE_TYPE_RECEIPT = "live_trigger_receipt"


AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_recommendation": False,
    "can_mutate_workflow_state": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "live_trigger_awareness_only",
}


SYNTHETIC_CASES: List[Dict[str, Any]] = [
    {
        "symbol": "XLE",
        "headline": "Energy disruption event triggers necessity-sector rebound",
        "price_change_pct": 2.4,
        "price": 58.05,
        "reference_price": 58.05,
        "sector": "energy",
        "confirmation": "confirmed",
    },
    {
        "symbol": "XLP",
        "headline": "Staples demand rises after regional supply concern",
        "price_change_pct": 1.7,
        "price": 83.42,
        "reference_price": 83.42,
        "sector": "consumer_staples",
        "confirmation": "confirmed",
    },
    {
        "symbol": "XLU",
        "headline": "Utilities stabilize as grid reliability concerns increase",
        "price_change_pct": 1.9,
        "price": 69.18,
        "reference_price": 69.18,
        "sector": "utilities",
        "confirmation": "partial",
    },
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(ts: Optional[datetime] = None) -> str:
    value = ts or utc_now()
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _normalize_payload(
    *,
    payload: Dict[str, Any],
    persistence_type: str,
    mutation_class: str,
    advisory_only: bool,
) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = mutation_class
    normalized["advisory_only"] = advisory_only
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    normalized["pm_authority_mutation_allowed"] = False
    normalized["sealed"] = True
    return normalized


def _governed_write(
    *,
    path: Path,
    payload: Dict[str, Any],
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
    advisory_only: bool = True,
) -> str:
    normalized = _normalize_payload(
        payload=payload,
        persistence_type=persistence_type,
        mutation_class=mutation_class,
        advisory_only=advisory_only,
    )

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": advisory_only,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def write_json(path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        payload = {"value": payload}

    _governed_write(
        path=path,
        payload=payload,
        persistence_type=PERSISTENCE_TYPE_STATE,
    )


def parse_api_key_from_json_map(raw: str) -> Optional[str]:
    try:
        value = json.loads(raw)
    except Exception:
        return None

    if isinstance(value, dict):
        for _, item in value.items():
            if isinstance(item, str) and item.strip():
                return item.strip()

    return None


def resolve_api_key() -> Optional[str]:
    explicit = os.getenv("AI_GO_LIVE_TRIGGER_API_KEY", "").strip()
    if explicit:
        return explicit

    single = os.getenv("AI_GO_API_KEY", "").strip()
    if single:
        return single

    mapped = os.getenv("AI_GO_API_KEYS_JSON", "").strip()
    if mapped:
        return parse_api_key_from_json_map(mapped)

    return None


def resolve_api_url() -> str:
    return os.getenv("AI_GO_LIVE_TRIGGER_URL", DEFAULT_URL).strip() or DEFAULT_URL


def resolve_timeout_seconds() -> int:
    raw = os.getenv("AI_GO_LIVE_TRIGGER_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS

    try:
        value = int(raw)
    except Exception:
        return DEFAULT_TIMEOUT_SECONDS

    return max(1, min(value, 300))


def build_default_state() -> Dict[str, Any]:
    return {
        "artifact_type": "live_trigger_state",
        "artifact_version": "northstar_live_trigger_v1",
        "last_case_index": -1,
        "last_request_id": "",
        "last_trigger_time": "",
        "last_status": "never_run",
        "success_count": 0,
        "failure_count": 0,
        "classification": {
            "persistence_type": PERSISTENCE_TYPE_STATE,
            "mutation_class": MUTATION_CLASS,
            "advisory_only": True,
            "execution_allowed": False,
        },
        "authority": dict(AUTHORITY_METADATA),
    }


def load_state() -> Dict[str, Any]:
    payload = read_json(STATE_PATH, build_default_state())
    return payload if isinstance(payload, dict) else build_default_state()


def select_case(state: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
    last_index = int(state.get("last_case_index", -1) or -1)
    next_index = (last_index + 1) % len(SYNTHETIC_CASES)
    return next_index, dict(SYNTHETIC_CASES[next_index])


def build_live_request(case: Dict[str, Any]) -> Dict[str, Any]:
    request_id = f"synthetic-live-{utc_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"

    return {
        "request_id": request_id,
        "source": "synthetic_live_trigger",
        "symbol": case.get("symbol"),
        "headline": case.get("headline"),
        "price_change_pct": case.get("price_change_pct"),
        "price": case.get("price"),
        "reference_price": case.get("reference_price"),
        "sector": case.get("sector"),
        "confirmation": case.get("confirmation"),
        "observed_at": utc_iso(),
        "advisory_only": True,
        "execution_allowed": False,
    }


def post_live_request(request_payload: Dict[str, Any]) -> Dict[str, Any]:
    api_key = resolve_api_key()
    url = resolve_api_url()

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers[DEFAULT_API_KEY_HEADER] = api_key

    request = urllib.request.Request(
        url=url,
        data=json.dumps(request_payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=resolve_timeout_seconds()) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body) if body else {}
            return {
                "status": "ok",
                "http_status": getattr(response, "status", 200),
                "response": payload,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {"raw_body": body}

        return {
            "status": "failed",
            "http_status": exc.code,
            "response": payload,
            "error": f"HTTPError:{exc.code}",
        }
    except Exception as exc:
        return {
            "status": "failed",
            "http_status": None,
            "response": {},
            "error": f"{type(exc).__name__}: {exc}",
        }


def build_receipt(
    *,
    state_before: Dict[str, Any],
    selected_index: int,
    request_payload: Dict[str, Any],
    api_result: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "live_trigger_receipt",
        "artifact_version": "northstar_live_trigger_v1",
        "receipt_id": f"live_trigger_receipt_{utc_now().strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}",
        "created_at": utc_iso(),
        "selected_case_index": selected_index,
        "request_id": request_payload.get("request_id"),
        "symbol": request_payload.get("symbol"),
        "target_url": resolve_api_url(),
        "status": api_result.get("status"),
        "http_status": api_result.get("http_status"),
        "error": api_result.get("error"),
        "state_before": {
            "last_case_index": state_before.get("last_case_index"),
            "success_count": state_before.get("success_count", 0),
            "failure_count": state_before.get("failure_count", 0),
        },
        "classification": {
            "persistence_type": PERSISTENCE_TYPE_RECEIPT,
            "mutation_class": RECEIPT_MUTATION_CLASS,
            "advisory_only": False,
            "execution_allowed": False,
        },
        "authority": dict(AUTHORITY_METADATA),
    }


def build_next_state(
    *,
    state_before: Dict[str, Any],
    selected_index: int,
    request_payload: Dict[str, Any],
    api_result: Dict[str, Any],
) -> Dict[str, Any]:
    state = dict(state_before)
    status = str(api_result.get("status", "failed"))

    state["artifact_type"] = "live_trigger_state"
    state["artifact_version"] = "northstar_live_trigger_v1"
    state["last_case_index"] = selected_index
    state["last_request_id"] = str(request_payload.get("request_id", ""))
    state["last_trigger_time"] = utc_iso()
    state["last_status"] = status
    state["classification"] = {
        "persistence_type": PERSISTENCE_TYPE_STATE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "execution_allowed": False,
    }
    state["authority"] = dict(AUTHORITY_METADATA)

    if status == "ok":
        state["success_count"] = int(state.get("success_count", 0) or 0) + 1
    else:
        state["failure_count"] = int(state.get("failure_count", 0) or 0) + 1

    return state


def persist_live_trigger_outputs(
    *,
    state: Dict[str, Any],
    latest_response: Dict[str, Any],
    receipt: Dict[str, Any],
) -> Dict[str, str]:
    state_path = _governed_write(
        path=STATE_PATH,
        payload=state,
        persistence_type=PERSISTENCE_TYPE_STATE,
    )

    response_path = _governed_write(
        path=LATEST_RESPONSE_PATH,
        payload={
            "artifact_type": "latest_live_trigger_response",
            "artifact_version": "northstar_live_trigger_v1",
            "recorded_at": utc_iso(),
            "response": latest_response,
            "classification": {
                "persistence_type": PERSISTENCE_TYPE_RESPONSE,
                "mutation_class": MUTATION_CLASS,
                "advisory_only": True,
                "execution_allowed": False,
            },
            "authority": dict(AUTHORITY_METADATA),
        },
        persistence_type=PERSISTENCE_TYPE_RESPONSE,
    )

    receipt_id = str(receipt.get("receipt_id", "live_trigger_receipt_unknown"))
    receipt_path = _governed_write(
        path=RECEIPTS_DIR / f"{receipt_id}.json",
        payload=receipt,
        persistence_type=PERSISTENCE_TYPE_RECEIPT,
        mutation_class=RECEIPT_MUTATION_CLASS,
        advisory_only=False,
    )

    return {
        "state_path": state_path,
        "latest_response_path": response_path,
        "receipt_path": receipt_path,
    }


def run_synthetic_live_trigger() -> Dict[str, Any]:
    state_before = load_state()
    selected_index, selected_case = select_case(state_before)
    request_payload = build_live_request(selected_case)
    api_result = post_live_request(request_payload)

    receipt = build_receipt(
        state_before=state_before,
        selected_index=selected_index,
        request_payload=request_payload,
        api_result=api_result,
    )

    next_state = build_next_state(
        state_before=state_before,
        selected_index=selected_index,
        request_payload=request_payload,
        api_result=api_result,
    )

    paths = persist_live_trigger_outputs(
        state=next_state,
        latest_response=api_result,
        receipt=receipt,
    )

    return {
        "status": api_result.get("status"),
        "request_id": request_payload.get("request_id"),
        "selected_case_index": selected_index,
        "symbol": request_payload.get("symbol"),
        "http_status": api_result.get("http_status"),
        "paths": paths,
        "receipt": receipt,
        "advisory_only": True,
        "execution_allowed": False,
    }


def run_once() -> Dict[str, Any]:
    return run_synthetic_live_trigger()


def main() -> None:
    print(json.dumps(run_synthetic_live_trigger(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
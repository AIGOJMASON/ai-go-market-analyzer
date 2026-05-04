from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root
from AI_GO.trade_tracking.performance.performance_runtime import build_performance_summary
from AI_GO.trade_tracking.trade_receipt_builder import build_performance_receipt


MUTATION_CLASS = "trade_tracking_performance_persistence"
PERSISTENCE_TYPE = "trade_tracking_performance_summary"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_source_events": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "trade_tracking_performance_summary",
}


def _trade_tracking_root() -> Path:
    return state_root() / "trade_tracking"


def _current_dir() -> Path:
    return _trade_tracking_root() / "current"


def _receipts_dir() -> Path:
    return _trade_tracking_root() / "db" / "receipts"


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "trade_tracking_performance_summary")
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = False
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_payload(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
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


def write_latest_performance_summary(system_id: str = "system_a") -> Dict[str, Any]:
    current_dir = _current_dir()
    receipts_dir = _receipts_dir()
    current_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)

    summary = _normalize_payload(build_performance_summary(system_id=system_id))

    current_path = current_dir / "latest_performance_summary.json"
    summary_path = _governed_write(current_path, summary)

    receipt = build_performance_receipt(
        system_id=system_id,
        generated_at=summary["generated_at"],
        path=summary_path,
    )
    receipt = {
        **receipt,
        "persistence_type": "trade_tracking_performance_receipt",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "execution_allowed": False,
    }

    receipt_path = receipts_dir / f'{receipt["receipt_id"]}.json'
    written_receipt_path = _governed_write(receipt_path, receipt)

    return {
        "status": "written",
        "summary": summary,
        "summary_path": summary_path,
        "receipt": receipt,
        "receipt_path": written_receipt_path,
    }
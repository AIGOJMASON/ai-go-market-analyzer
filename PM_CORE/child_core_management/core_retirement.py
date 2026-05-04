from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json

from .child_core_registry import PM_CORE_DIR, get_entry, retire_core, update_core_entry


RECEIPTS_DIR = PM_CORE_DIR / "state" / "receipts"
RETIREMENT_VERSION = "northstar_child_core_retirement_v1"
MUTATION_CLASS = "receipt"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_retire_child_core_without_governance": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_child_core_retirement_receipt_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "pm_child_core_retirement_receipt")
    normalized.setdefault("artifact_version", RETIREMENT_VERSION)
    normalized["persistence_type"] = "pm_child_core_retirement_receipt"
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = False
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["approval_required"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_payload(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": "pm_child_core_retirement_receipt",
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


def _retirement_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__retirement_receipt.json"


def retire_child_core(
    core_id: str,
    *,
    reason: str,
    operator: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    if entry.get("status") == "retired":
        raise ValueError(f"Child core '{core_id}' is already retired.")

    retired_at = _utc_now()

    receipt = {
        "artifact_type": "pm_child_core_retirement_receipt",
        "artifact_version": RETIREMENT_VERSION,
        "status": "child_core_retired",
        "core_id": core_id,
        "reason": reason,
        "operator": operator,
        "notes": notes,
        "retired_at": retired_at,
        "prior_status": entry.get("status"),
        "core_path": entry.get("core_path"),
        "activation_receipt_path": entry.get("activation_receipt_path"),
        "governance_note": "Retirement is registry state only and does not execute child-core shutdown actions.",
    }

    receipt_path = _retirement_receipt_path(core_id)
    written_receipt_path = _governed_write(receipt_path, receipt)

    updated = retire_core(
        core_id,
        written_receipt_path,
        notes=notes or reason,
    )
    update_core_entry(core_id, {"updated_at": retired_at})

    return {
        "status": "retired",
        "core_id": core_id,
        "retirement_receipt_path": written_receipt_path,
        "registry_entry": updated,
    }
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json


PM_CORE_DIR = Path(__file__).resolve().parent
STATE_DIR = PM_CORE_DIR / "state" / "current"
DOMAIN_ALIGNMENT_PATH = STATE_DIR / "pm_domain_alignment.json"

DOMAIN_ALIGNMENT_VERSION = "northstar_pm_domain_alignment_v1"
MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "pm_domain_alignment_record"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_route_directly": False,
    "can_activate_child_core": False,
    "can_mutate_workflow_state": False,
    "can_override_research_truth": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_domain_alignment_awareness_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_type", "pm_domain_alignment_record")
    normalized.setdefault("artifact_version", DOMAIN_ALIGNMENT_VERSION)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["routing_execution_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
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
        "advisory_only": True,
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


def build_domain_alignment_record(
    *,
    domain_focus: str,
    target_child_core_id: str = "",
    recommended_action: str = "review",
    rationale: str = "",
    source_record_id: Optional[str] = None,
) -> Dict[str, Any]:
    return _normalize_payload(
        {
            "artifact_type": "pm_domain_alignment_record",
            "artifact_version": DOMAIN_ALIGNMENT_VERSION,
            "record_id": f"pm_domain_alignment_{_utc_now().replace(':', '-')}",
            "created_at": _utc_now(),
            "domain_focus": str(domain_focus or "").strip(),
            "target_child_core_id": str(target_child_core_id or "").strip(),
            "recommended_action": str(recommended_action or "review").strip(),
            "rationale": str(rationale or "").strip(),
            "source_record_id": source_record_id,
            "alignment_status": "advisory",
        }
    )


def persist_domain_alignment_record(record: Dict[str, Any]) -> Dict[str, Any]:
    current = _normalize_payload(_read_json(DOMAIN_ALIGNMENT_PATH, {"records": []}))
    records = current.get("records", [])
    if not isinstance(records, list):
        records = []

    normalized_record = _normalize_payload(record)
    normalized_record["persistence_type"] = "pm_domain_alignment_entry"

    records.append(normalized_record)

    current["records"] = records[-1000:]
    current["updated_at"] = _utc_now()

    path = _governed_write(DOMAIN_ALIGNMENT_PATH, current)

    return {
        "status": "persisted",
        "path": path,
        "record": normalized_record,
    }


def align_domain(
    *,
    domain_focus: str,
    target_child_core_id: str = "",
    recommended_action: str = "review",
    rationale: str = "",
    source_record_id: Optional[str] = None,
) -> Dict[str, Any]:
    record = build_domain_alignment_record(
        domain_focus=domain_focus,
        target_child_core_id=target_child_core_id,
        recommended_action=recommended_action,
        rationale=rationale,
        source_record_id=source_record_id,
    )
    return persist_domain_alignment_record(record)


def load_domain_alignment_records() -> Dict[str, Any]:
    return _normalize_payload(_read_json(DOMAIN_ALIGNMENT_PATH, {"records": []}))
from __future__ import annotations

import inspect
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json

try:
    from AI_GO.core.shared.ids import make_id
except Exception:
    def make_id(prefix: str = "WR-RESEARCH-PACKET") -> str:
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{prefix}-{stamp}"


try:
    from AI_GO.core.shared.timestamps import utc_now_iso
except Exception:
    def utc_now_iso() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


try:
    from AI_GO.core.shared.paths import get_project_root
except Exception:
    def get_project_root() -> Path:
        return Path(__file__).resolve().parents[3]


RESEARCH_PACKET_PREFIX = "WR-RESEARCH-PACKET"
PACKET_SUBDIR = Path("packets") / "research"

MUTATION_CLASS = "source_signal_persistence"
PERSISTENCE_TYPE = "research_packet"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_pm_authority": False,
    "can_override_research_truth": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "research_packet_truth_only",
}


def _normalize_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = deepcopy(packet)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["pm_authority_mutation_allowed"] = False
    normalized["workflow_mutation_allowed"] = False
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
    normalized = _normalize_packet(payload)

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


def build_research_packet(
    intake_record: Dict[str, Any],
    screening_result: Dict[str, Any],
    trust_result: Dict[str, Any],
    *,
    packet_id: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_packet_id = packet_id or make_id(RESEARCH_PACKET_PREFIX)

    packet = {
        "packet_id": resolved_packet_id,
        "packet_type": "research_packet",
        "issuing_authority": "RESEARCH_CORE",
        "created_at": utc_now_iso(),
        "title": str(intake_record.get("title", "") or intake_record.get("query", "")).strip(),
        "summary": str(intake_record.get("summary", "") or intake_record.get("query", "")).strip(),
        "source_refs": deepcopy(intake_record.get("source_refs", [])),
        "scope": deepcopy(intake_record.get("scope", {})),
        "tags": deepcopy(intake_record.get("tags", [])),
        "intake_record": deepcopy(intake_record),
        "screening_result": deepcopy(screening_result),
        "trust_result": deepcopy(trust_result),
    }

    return _normalize_packet(packet)


def validate_research_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "packet_id",
        "packet_type",
        "issuing_authority",
        "created_at",
        "title",
        "summary",
        "source_refs",
        "scope",
        "tags",
        "intake_record",
        "screening_result",
        "trust_result",
        "persistence_type",
        "mutation_class",
        "advisory_only",
    ]

    missing = [field for field in required if field not in packet]

    return {
        "artifact_type": "research_packet_validation",
        "valid": not missing and packet.get("mutation_class") == MUTATION_CLASS,
        "missing": missing,
        "advisory_only": True,
        "can_execute": False,
    }


def persist_research_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _normalize_packet(packet)
    validation = validate_research_packet(normalized)

    if validation.get("valid") is not True:
        return {
            "status": "rejected",
            "reason": "invalid_research_packet",
            "validation": validation,
            "packet": normalized,
        }

    root = get_project_root()
    path = root / PACKET_SUBDIR / f"{normalized['packet_id']}.json"
    written_path = _governed_write(path, normalized)

    return {
        "status": "persisted",
        "packet_id": normalized["packet_id"],
        "packet_path": written_path,
        "validation": validation,
        "packet": normalized,
    }


def build_and_persist_research_packet(
    intake_record: Dict[str, Any],
    screening_result: Dict[str, Any],
    trust_result: Dict[str, Any],
    *,
    packet_id: Optional[str] = None,
) -> Dict[str, Any]:
    packet = build_research_packet(
        intake_record=intake_record,
        screening_result=screening_result,
        trust_result=trust_result,
        packet_id=packet_id,
    )
    return persist_research_packet(packet)
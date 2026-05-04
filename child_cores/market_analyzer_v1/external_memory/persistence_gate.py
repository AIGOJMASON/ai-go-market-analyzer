from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json


class PersistenceGateError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _state_dir() -> Path:
    return _root_dir() / "state" / "external_memory" / "market_analyzer_v1"


def _gate_receipts_dir() -> Path:
    return _state_dir() / "persistence_gate_receipts"


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _persist_gate_receipt(path: Path, payload: Dict[str, Any]) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="external_memory_persistence_gate",
        persistence_type="external_memory_persistence_gate_receipt",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_external_memory_persistence_gate_receipt",
            "child_core_id": "market_analyzer_v1",
            "layer": "external_memory.persistence_gate",
        },
    )


def _build_receipt_id(record_id: str, decision: str) -> str:
    digest = sha256(f"{record_id}|{decision}|persistence_gate".encode("utf-8")).hexdigest()[:12]
    return f"persistence_gate_{record_id}_{digest}"


def _qualification_decision(qualification_result: Dict[str, Any]) -> str:
    return _safe_str(
        qualification_result.get("decision")
        or _as_dict(qualification_result.get("external_memory_qualification_artifact")).get("decision")
    )


def _qualification_status(qualification_result: Dict[str, Any]) -> str:
    return _safe_str(
        qualification_result.get("status")
        or _as_dict(qualification_result.get("external_memory_qualification_artifact")).get("status")
    )


def _qualification_score(qualification_result: Dict[str, Any]) -> int:
    raw = (
        qualification_result.get("score")
        or _as_dict(qualification_result.get("external_memory_qualification_artifact")).get("score")
        or 0
    )
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def run_persistence_gate(
    external_memory_ingress_record: Dict[str, Any],
    qualification_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(external_memory_ingress_record, dict):
        raise PersistenceGateError("external_memory_ingress_record must be a dict")
    if not isinstance(qualification_result, dict):
        raise PersistenceGateError("qualification_result must be a dict")

    record = deepcopy(external_memory_ingress_record)
    qualification = deepcopy(qualification_result)

    record_id = _safe_str(record.get("record_id"))
    if not record_id:
        raise PersistenceGateError("external_memory_ingress_record is missing record_id")

    decision = _qualification_decision(qualification)
    status = _qualification_status(qualification)
    score = _qualification_score(qualification)

    allow_persist = decision == "accept" and status in {"accepted", "passed", "ok"} and score >= 1
    blocked_reason = "" if allow_persist else "qualification_not_accepted"

    artifact = {
        "artifact_type": "external_memory_persistence_gate_artifact",
        "artifact_version": "v1",
        "record_id": record_id,
        "created_at": _utc_now_iso(),
        "allow_persist": allow_persist,
        "decision": "allow" if allow_persist else "block",
        "blocked_reason": blocked_reason,
        "qualification_score": score,
        "qualification_decision": decision,
        "qualification_status": status,
        "classification": {
            "persistence_type": "external_memory_persistence_gate",
            "mutation_class": "external_memory_persistence_gate",
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "authority_mutation_allowed": False,
            "advisory_only": True,
        },
        "authority": {
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_runtime": False,
            "can_mutate_recommendations": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
        },
        "sealed": True,
    }

    receipt_id = _build_receipt_id(record_id, artifact["decision"])
    receipt_path = _gate_receipts_dir() / f"{receipt_id}.json"

    receipt = {
        "receipt_id": receipt_id,
        "receipt_type": "external_memory_persistence_gate_receipt",
        "receipt_version": "v1",
        "status": "passed" if allow_persist else "blocked",
        "created_at": artifact["created_at"],
        "record_id": record_id,
        "allow_persist": allow_persist,
        "blocked_reason": blocked_reason,
        "artifact": artifact,
        "artifact_path": str(receipt_path),
        "sealed": True,
    }

    _persist_gate_receipt(receipt_path, receipt)

    return {
        "status": "passed" if allow_persist else "blocked",
        "allow_persist": allow_persist,
        "blocked_reason": blocked_reason,
        "record_id": record_id,
        "receipt_id": receipt_id,
        "receipt_path": str(receipt_path),
        "external_memory_persistence_gate_artifact": artifact,
        "external_memory_persistence_gate_receipt": receipt,
        "sealed": True,
    }
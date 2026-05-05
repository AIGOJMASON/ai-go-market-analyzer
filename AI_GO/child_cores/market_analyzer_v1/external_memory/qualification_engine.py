from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json


class QualificationEngineError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _state_dir() -> Path:
    return _root_dir() / "state" / "external_memory" / "market_analyzer_v1"


def _qualification_receipts_dir() -> Path:
    return _state_dir() / "qualification_receipts"


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return bool(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _persist_receipt(path: Path, payload: Dict[str, Any]) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="external_memory_qualification",
        persistence_type="external_memory_qualification_receipt",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_external_memory_qualification_receipt",
            "child_core_id": "market_analyzer_v1",
            "layer": "external_memory.qualification_engine",
        },
    )


def _build_receipt_id(record_id: str, score: int) -> str:
    digest = sha256(f"{record_id}|{score}|qualification".encode("utf-8")).hexdigest()[:12]
    return f"qualification_{record_id}_{digest}"


def _score_record(record: Dict[str, Any]) -> int:
    score = 0

    if _safe_str(record.get("record_id")):
        score += 20

    if _safe_str(record.get("target_child_core_id")) == "market_analyzer_v1":
        score += 20

    if _safe_str(record.get("source_type")):
        score += 10

    if _safe_str(record.get("symbol")):
        score += 15

    if _safe_str(record.get("event_theme")):
        score += 15

    if _safe_str(record.get("trust_class")):
        score += 10

    if _as_list(record.get("source_refs")):
        score += 10

    authority = _as_dict(record.get("authority"))
    if authority:
        if authority.get("execution_allowed") is False or authority.get("can_execute") is False:
            score += 5
        if authority.get("raw_provider_payload_allowed") is False:
            score += 5

    if _safe_bool(record.get("sealed"), default=False):
        score += 5

    return score


def run_qualification_engine(external_memory_ingress_record: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(external_memory_ingress_record, dict):
        raise QualificationEngineError("external_memory_ingress_record must be a dict")

    record = deepcopy(external_memory_ingress_record)
    record_id = _safe_str(record.get("record_id"))
    if not record_id:
        raise QualificationEngineError("external_memory_ingress_record is missing record_id")

    score = _score_record(record)
    accepted = score >= 60
    decision = "accept" if accepted else "reject"
    status = "accepted" if accepted else "rejected"
    created_at = _utc_now_iso()

    artifact = {
        "artifact_type": "external_memory_qualification_artifact",
        "artifact_version": "v1",
        "record_id": record_id,
        "created_at": created_at,
        "score": score,
        "decision": decision,
        "status": status,
        "required_target_child_core_id": "market_analyzer_v1",
        "classification": {
            "persistence_type": "external_memory_qualification",
            "mutation_class": "external_memory_qualification",
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

    receipt_id = _build_receipt_id(record_id, score)
    receipt_path = _qualification_receipts_dir() / f"{receipt_id}.json"

    receipt = {
        "receipt_id": receipt_id,
        "receipt_type": "external_memory_qualification_receipt",
        "receipt_version": "v1",
        "status": status,
        "created_at": created_at,
        "record_id": record_id,
        "score": score,
        "decision": decision,
        "artifact_path": str(receipt_path),
        "external_memory_qualification_artifact": artifact,
        "sealed": True,
    }

    _persist_receipt(receipt_path, receipt)

    return {
        "status": status,
        "decision": decision,
        "score": score,
        "record_id": record_id,
        "receipt_id": receipt_id,
        "receipt_path": str(receipt_path),
        "external_memory_qualification_artifact": artifact,
        "external_memory_qualification_receipt": receipt,
        "sealed": True,
    }
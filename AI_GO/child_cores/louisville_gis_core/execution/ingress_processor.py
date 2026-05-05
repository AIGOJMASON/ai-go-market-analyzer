from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


INGRESS_PROCESSOR_VERSION = "northstar_louisville_gis_ingress_v1"

ALLOWED_INGRESS_TYPES = {
    "gis_parcel_request",
    "gis_zoning_request",
    "gis_permit_request",
    "gis_address_lookup",
    "gis_operator_request",
    "root_handoff_packet",
}

REJECTED_SOURCES = {
    "unverified_external_feed",
    "raw_provider_payload",
    "unbounded_user_input",
}


class LouisvilleGISIngressError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _state_root() -> Path:
    return state_root() / "louisville_gis_core"


def _ingress_root() -> Path:
    return _state_root() / "ingress"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "louisville_gis_ingress_record",
        "mutation_class": "louisville_gis_ingress_persistence",
        "advisory_only": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "louisville_gis_core_ingress_processor",
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
    }


def _persist_ingress_record(record: Dict[str, Any]) -> Path:
    request_id = _safe_str(record.get("request_id")) or "unknown_request"
    path = _ingress_root() / f"{request_id}.json"

    governed_write_json(
        path=path,
        payload=record,
        mutation_class="louisville_gis_ingress_persistence",
        persistence_type="louisville_gis_ingress_record",
        authority_metadata={
            "authority_id": "northstar_stage_6a",
            "operation": "persist_louisville_gis_ingress_record",
            "child_core_id": "louisville_gis_core",
            "layer": "execution.ingress_processor",
        },
    )

    return path


def validate_ingress_payload(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise LouisvilleGISIngressError("payload must be a dict")

    request_id = _safe_str(payload.get("request_id"))
    if not request_id:
        raise LouisvilleGISIngressError("request_id is required")

    ingress_type = _safe_str(payload.get("ingress_type") or payload.get("artifact_type"))
    if ingress_type and ingress_type not in ALLOWED_INGRESS_TYPES:
        raise LouisvilleGISIngressError(f"unsupported ingress_type: {ingress_type}")

    source = _safe_str(payload.get("source"))
    if source in REJECTED_SOURCES:
        raise LouisvilleGISIngressError(f"rejected ingress source: {source}")


def build_ingress_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    validate_ingress_payload(payload)

    request_id = _safe_str(payload.get("request_id"))
    ingress_type = _safe_str(payload.get("ingress_type") or payload.get("artifact_type")) or "gis_operator_request"

    return {
        "artifact_type": "louisville_gis_ingress_record",
        "artifact_version": INGRESS_PROCESSOR_VERSION,
        "status": "accepted",
        "request_id": request_id,
        "ingress_type": ingress_type,
        "created_at": _utc_now_iso(),
        "source": _safe_str(payload.get("source")) or "operator",
        "target_core": "louisville_gis_core",
        "payload": _safe_dict(payload.get("payload")) or {
            key: deepcopy(value)
            for key, value in payload.items()
            if key not in {"payload"}
        },
        "source_refs": _safe_list(payload.get("source_refs")),
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def process_ingress(payload: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
    record = build_ingress_record(payload)

    output_path = ""
    if persist:
        output_path = str(_persist_ingress_record(record))

    return {
        "status": "accepted",
        "request_id": record["request_id"],
        "record": record,
        "record_path": output_path,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }


def run_ingress_processor(payload: Dict[str, Any]) -> Dict[str, Any]:
    return process_ingress(payload, persist=True)

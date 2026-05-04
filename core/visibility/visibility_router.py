from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json

from .collectors.runtime_collector import collect_runtime_view
from .collectors.watcher_smi_collector import collect_watcher_view, collect_smi_view
from .collectors.external_memory_collector import collect_external_memory_view
from .collectors.inventory_collector import collect_inventory_view
from .normalizers.summary_normalizer import build_summary
from .receipts.visibility_generation_receipt import (
    build_generation_receipt,
    persist_generation_receipt,
)


MUTATION_CLASS = "visibility_persistence"
PERSISTENCE_TYPE = "system_visibility_packet"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "system_visibility_only",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = PROJECT_ROOT / "state" / "system_visibility"
PACKET_PATH = STATE_ROOT / "SYSTEM_EYES_PACKET.latest.json"
RECEIPT_DIR = STATE_ROOT / "generation_receipts"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_visibility_state_dirs() -> None:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(packet)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_influence"] = False
    normalized["runtime_mutation_allowed"] = False
    normalized["recommendation_mutation_allowed"] = False
    normalized["visibility_mode"] = "read_only"
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
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
        return governed_write_json(**kwargs)

    if accepted:
        return governed_write_json(**accepted)

    return governed_write_json(path, normalized)


def build_system_eyes_packet() -> Dict[str, Any]:
    ensure_visibility_state_dirs()

    runtime_view = collect_runtime_view()
    watcher_view = collect_watcher_view()
    smi_view = collect_smi_view()
    external_memory_view = collect_external_memory_view()
    inventory_view = collect_inventory_view()

    receipt = build_generation_receipt()
    receipt_path = persist_generation_receipt(receipt, RECEIPT_DIR)

    packet = _normalize_packet(
        {
            "packet_type": "system_eyes_packet",
            "contract_version": "1.0.0",
            "generated_at": utc_now_iso(),
            "system_version": "AI_GO",
            "generation_receipt": {
                **receipt,
                "path": str(receipt_path),
            },
            "summary": build_summary(
                {
                    "runtime_view": runtime_view,
                    "watcher_view": watcher_view,
                    "smi_view": smi_view,
                    "external_memory_view": external_memory_view,
                    "inventory_view": inventory_view,
                }
            ),
            "runtime_view": runtime_view,
            "watcher_view": watcher_view,
            "smi_view": smi_view,
            "external_memory_view": external_memory_view,
            "inventory_view": inventory_view,
        }
    )

    _governed_write(PACKET_PATH, packet)
    return packet


def persist_system_eyes_packet(packet: Dict[str, Any]) -> str:
    result = _governed_write(PACKET_PATH, packet)
    return str(
        result.get("path")
        if isinstance(result, dict) and result.get("path")
        else PACKET_PATH
    )
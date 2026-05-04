from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.paths.path_resolver import ensure_dir, get_state_root
from AI_GO.core.receipts.receipt_writer import sha256_text, stable_json_dumps, utc_now_compact


MUTATION_CLASS = "receipt"
PERSISTENCE_TYPE = "governance_packet"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "governance_audit_packet_only",
}


def _safe_slug(value: Any, *, fallback: str, max_len: int) -> str:
    raw = str(value or "").strip()
    chars = []

    for char in raw:
        if char.isalnum() or char in {"_", "-"}:
            chars.append(char)
        elif char in {" ", ".", "/", "\\", ":"}:
            chars.append("_")

    slug = "".join(chars).strip("_-")
    while "__" in slug:
        slug = slug.replace("__", "_")

    slug = slug or fallback
    return slug[:max_len].strip("_-") or fallback


def _governance_packet_root() -> Path:
    return ensure_dir(get_state_root() / "governance_packets")


def _profile_root(profile: str) -> Path:
    clean_profile = _safe_slug(profile, fallback="general", max_len=64)
    return ensure_dir(_governance_packet_root() / clean_profile)


def build_governance_packet_id(
    *,
    profile: str,
    action: str,
    project_id: Optional[str] = None,
    phase_id: Optional[str] = None,
) -> str:
    clean_profile = _safe_slug(profile, fallback="profile", max_len=48)
    clean_action = _safe_slug(action, fallback="request", max_len=48)
    clean_project = _safe_slug(project_id or "no_project", fallback="no_project", max_len=80)
    clean_phase = _safe_slug(phase_id or "no_phase", fallback="no_phase", max_len=80)

    return (
        f"governance-{clean_profile}-{clean_action}-"
        f"{clean_project}-{clean_phase}-{utc_now_compact()}"
    )


def build_governance_packet_filename(
    *,
    profile: str,
    action: str,
) -> str:
    clean_profile = _safe_slug(profile, fallback="profile", max_len=36)
    clean_action = _safe_slug(action, fallback="request", max_len=36)
    return f"{clean_profile}-{clean_action}-{utc_now_compact()}.json"


def _normalize_packet(packet: Dict[str, Any], packet_id: str) -> Dict[str, Any]:
    output_packet = dict(packet)
    output_packet["governance_packet_id"] = packet_id
    output_packet["persistence_type"] = PERSISTENCE_TYPE
    output_packet["mutation_class"] = MUTATION_CLASS
    output_packet["advisory_only"] = False
    output_packet["authority_metadata"] = dict(AUTHORITY_METADATA)

    body_without_integrity = dict(output_packet)
    body_without_integrity.pop("integrity", None)

    payload_hash = sha256_text(stable_json_dumps(body_without_integrity))
    output_packet["integrity"] = {
        "hash_algorithm": "sha256",
        "payload_hash": payload_hash,
        "hash_scope": "governance_packet_without_integrity",
    }

    return output_packet


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
    kwargs = {
        "path": path,
        "output_path": path,
        "payload": payload,
        "data": payload,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": False,
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
        return governed_write_json(**kwargs)

    if accepted:
        return governed_write_json(**accepted)

    return governed_write_json(path, payload)


def persist_governance_packet(
    *,
    packet: Dict[str, Any],
    profile: str,
    governance_packet_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")

    packet_id = governance_packet_id or str(packet.get("governance_packet_id", "")).strip()
    if not packet_id:
        packet_id = build_governance_packet_id(
            profile=profile,
            action=str(packet.get("action", "request")),
            project_id=str(packet.get("project_id", "")),
            phase_id=str(packet.get("phase_id", "")),
        )

    output_packet = _normalize_packet(packet, packet_id)

    filename = build_governance_packet_filename(
        profile=profile,
        action=str(output_packet.get("action", "request")),
    )
    path = _profile_root(profile) / filename

    result = _governed_write(path, output_packet)

    return {
        "status": "persisted",
        "governance_packet_id": packet_id,
        "filename": filename,
        "path": str(
            result.get("path")
            if isinstance(result, dict) and result.get("path")
            else path
        ),
        "payload_hash": output_packet["integrity"]["payload_hash"],
        "packet": output_packet,
    }


def load_governance_packet(
    *,
    profile: str,
    governance_packet_id: str,
) -> Dict[str, Any]:
    clean_id = str(governance_packet_id or "").strip()
    if not clean_id:
        raise ValueError("governance_packet_id is required")

    root = _profile_root(profile)

    for path in sorted(root.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(payload, dict) and payload.get("governance_packet_id") == clean_id:
            payload["_loaded_from_path"] = str(path)
            return payload

    raise FileNotFoundError(f"governance_packet_not_found:{clean_id}")


def attach_result_summary_to_governance_packet(
    *,
    profile: str,
    governance_packet_id: str,
    result_summary: Dict[str, Any],
) -> Dict[str, Any]:
    clean_id = str(governance_packet_id or "").strip()
    if not clean_id:
        raise ValueError("governance_packet_id is required")

    if not isinstance(result_summary, dict):
        raise ValueError("result_summary must be a dict")

    packet = load_governance_packet(
        profile=profile,
        governance_packet_id=clean_id,
    )

    packet.pop("_loaded_from_path", None)
    packet.pop("_loaded_from_index", None)
    packet.pop("_index_entry", None)

    packet["result_summary"] = dict(result_summary)
    packet["post_execution_result_summary_attached"] = True

    persisted = persist_governance_packet(
        packet=packet,
        profile=profile,
        governance_packet_id=clean_id,
    )

    return {
        "status": "attached",
        "governance_packet_id": clean_id,
        "path": persisted["path"],
        "payload_hash": persisted["payload_hash"],
        "result_summary": result_summary,
    }
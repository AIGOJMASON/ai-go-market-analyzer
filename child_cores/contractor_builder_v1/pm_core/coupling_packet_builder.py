from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


COUPLING_PACKET_VERSION = "v6c.1"
CHILD_CORE_ID = "contractor_builder_v1"
ISSUING_LAYER = "PM_CORE"

VALID_SERVICES = {
    "oracle",
    "decision",
    "risk",
    "router",
    "comply",
    "assumption",
}

ALLOWED_TARGETS = {
    "oracle": {"decision"},
    "decision": {"risk"},
    "risk": {"router"},
    "router": {"comply"},
    "assumption": {"oracle", "decision", "risk", "router", "comply"},
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_service(value: Any) -> str:
    return _clean_text(value).lower()


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _hash_payload(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_status(result: Dict[str, Any]) -> str:
    return _clean_text(
        result.get("status")
        or result.get("entry", {}).get("status")
        or result.get("entry", {}).get("decision_status")
        or result.get("packet", {}).get("status")
        or "unknown"
    )


def _extract_artifact_path(result: Dict[str, Any]) -> str:
    return _clean_text(
        result.get("artifact_path")
        or result.get("path")
        or result.get("record_path")
        or ""
    )


def _extract_receipt_refs(result: Dict[str, Any]) -> List[str]:
    refs: List[str] = []

    for key in ("receipt_path", "receipt_id"):
        value = _clean_text(result.get(key))
        if value:
            refs.append(value)

    receipt_paths = result.get("receipt_paths")
    if isinstance(receipt_paths, dict):
        for value in receipt_paths.values():
            clean = _clean_text(value)
            if clean:
                refs.append(clean)

    if isinstance(receipt_paths, list):
        for value in receipt_paths:
            clean = _clean_text(value)
            if clean:
                refs.append(clean)

    return refs


def _extract_result_summary_hash(result: Dict[str, Any]) -> str:
    summary = _as_dict(result.get("result_summary"))
    if not summary:
        return ""

    existing = _clean_text(summary.get("result_summary_hash"))
    if existing:
        return existing

    return _hash_payload(summary)


def _extract_source_id(source_service: str, result: Dict[str, Any]) -> str:
    entry = _as_dict(result.get("entry"))
    packet = _as_dict(result.get("packet"))

    candidates = [
        result.get("source_id"),
        result.get(f"{source_service}_id"),
        entry.get(f"{source_service}_id"),
        packet.get(f"{source_service}_id"),
        entry.get("decision_id"),
        entry.get("risk_id"),
        packet.get("change_packet_id"),
        result.get("artifact_id"),
        result.get("record_id"),
    ]

    for candidate in candidates:
        clean = _clean_text(candidate)
        if clean:
            return clean

    return f"{source_service}-{_hash_payload(result)[:12]}"


def _extract_governance_refs(result: Dict[str, Any]) -> Dict[str, Any]:
    state = _as_dict(result.get("state"))
    watcher = _as_dict(result.get("watcher"))
    execution_gate = _as_dict(result.get("execution_gate"))
    mutation_guard = _as_dict(result.get("mutation_guard"))

    return {
        "state_valid": state.get("valid") is True or result.get("state_valid") is True,
        "watcher_valid": watcher.get("valid") is True or result.get("watcher_valid") is True,
        "execution_gate_allowed": (
            execution_gate.get("allowed") is True
            or result.get("execution_gate_allowed") is True
        ),
        "mutation_guard_valid": (
            mutation_guard.get("valid") is True
            or mutation_guard.get("allowed") is True
            or result.get("mutation_guard_valid") is True
            or result.get("mode") == "governed_execution"
        ),
    }


def _validate_source_target(source_service: str, target_service: str) -> None:
    if source_service not in VALID_SERVICES:
        raise ValueError(f"invalid_source_service:{source_service}")

    if target_service not in VALID_SERVICES:
        raise ValueError(f"invalid_target_service:{target_service}")

    allowed_targets = ALLOWED_TARGETS.get(source_service, set())
    if target_service not in allowed_targets:
        raise ValueError(f"illegal_pm_coupling_path:{source_service}->{target_service}")


def build_pm_coupling_packet(
    *,
    project_id: str,
    source_service: str,
    target_service: str,
    source_result: Dict[str, Any],
    phase_id: str = "",
    actor: str = ISSUING_LAYER,
    influence_summary: str = "",
) -> Dict[str, Any]:
    normalized_source = _normalize_service(source_service)
    normalized_target = _normalize_service(target_service)

    _validate_source_target(normalized_source, normalized_target)

    source_payload = _as_dict(source_result)
    source_id = _extract_source_id(normalized_source, source_payload)
    source_hash = _hash_payload(source_payload)
    governance_refs = _extract_governance_refs(source_payload)

    packet_base: Dict[str, Any] = {
        "artifact_type": "contractor_pm_coupling_packet",
        "artifact_version": COUPLING_PACKET_VERSION,
        "created_at": _utc_now_iso(),
        "child_core_id": CHILD_CORE_ID,
        "issuing_layer": ISSUING_LAYER,
        "actor": _clean_text(actor) or ISSUING_LAYER,
        "project_id": _clean_text(project_id),
        "phase_id": _clean_text(phase_id),
        "source": {
            "source_type": normalized_source,
            "source_id": source_id,
            "source_status": _safe_status(source_payload),
            "source_hash": source_hash,
            "result_summary_hash": _extract_result_summary_hash(source_payload),
            "receipt_refs": _extract_receipt_refs(source_payload),
            "artifact_path": _extract_artifact_path(source_payload),
            "governance_refs": governance_refs,
        },
        "target": {
            "target_service": normalized_target,
            "target_mode": "context_influence_only",
            "must_revalidate": True,
        },
        "influence": {
            "summary": _clean_text(influence_summary),
            "may_inform_target": True,
            "may_execute_target": False,
            "may_mutate_target": False,
            "requires_target_governance": True,
        },
        "authority": {
            "pm_owned": True,
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "downstream_service_must_revalidate": True,
        },
        "sealed": True,
    }

    packet_base["packet_id"] = (
        f"pm-coupling-{normalized_source}-to-{normalized_target}-"
        f"{_hash_payload(packet_base)[:16]}"
    )

    packet_base["packet_hash"] = _hash_payload(
        {
            key: value
            for key, value in packet_base.items()
            if key != "packet_hash"
        }
    )

    return packet_base


def build_pm_coupling_context(
    *,
    project_id: str,
    phase_id: str = "",
    actor: str = ISSUING_LAYER,
    source_results: Optional[List[Dict[str, Any]]] = None,
    packets: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    resolved_project_id = _clean_text(project_id)
    built_packets: List[Dict[str, Any]] = []

    if packets:
        built_packets.extend([_as_dict(packet) for packet in packets if isinstance(packet, dict)])

    for item in _as_list(source_results):
        source_service = _normalize_service(item.get("source_service"))
        target_service = _normalize_service(item.get("target_service"))
        source_result = _as_dict(item.get("source_result"))

        built_packets.append(
            build_pm_coupling_packet(
                project_id=resolved_project_id,
                phase_id=phase_id,
                actor=actor,
                source_service=source_service,
                target_service=target_service,
                source_result=source_result,
                influence_summary=_clean_text(item.get("influence_summary")),
            )
        )

    by_target: Dict[str, List[Dict[str, Any]]] = {
        "oracle": [],
        "decision": [],
        "risk": [],
        "router": [],
        "comply": [],
        "assumption": [],
    }

    for packet in built_packets:
        target_service = packet.get("target", {}).get("target_service", "unknown")
        if target_service in by_target:
            by_target[target_service].append(packet)

    context: Dict[str, Any] = {
        "artifact_type": "contractor_pm_coupling_context",
        "artifact_version": COUPLING_PACKET_VERSION,
        "created_at": _utc_now_iso(),
        "child_core_id": CHILD_CORE_ID,
        "issuing_layer": ISSUING_LAYER,
        "actor": _clean_text(actor) or ISSUING_LAYER,
        "project_id": resolved_project_id,
        "phase_id": _clean_text(phase_id),
        "packet_count": len(built_packets),
        "packets": built_packets,
        "by_target": by_target,
        "authority": {
            "pm_owned": True,
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "downstream_services_must_revalidate": True,
        },
        "sealed": True,
    }

    context["context_hash"] = _hash_payload(
        {
            key: value
            for key, value in context.items()
            if key != "context_hash"
        }
    )

    return context


def extract_target_context(
    *,
    coupling_context: Dict[str, Any],
    target_service: str,
) -> Dict[str, Any]:
    normalized_target = _normalize_service(target_service)
    context = _as_dict(coupling_context)
    by_target = _as_dict(context.get("by_target"))
    packets = _as_list(by_target.get(normalized_target))

    return {
        "artifact_type": "contractor_pm_target_coupling_context",
        "artifact_version": COUPLING_PACKET_VERSION,
        "created_at": _utc_now_iso(),
        "project_id": context.get("project_id", ""),
        "phase_id": context.get("phase_id", ""),
        "target_service": normalized_target,
        "packet_count": len(packets),
        "packets": packets,
        "authority": {
            "context_only": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "downstream_service_must_revalidate": True,
        },
        "sealed": True,
    }
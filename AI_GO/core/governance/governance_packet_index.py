from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.paths.path_resolver import ensure_dir, get_state_root
from AI_GO.core.receipts.receipt_writer import sha256_text, stable_json_dumps


INDEX_VERSION = "v1"
AWARENESS_VERSION = "v1"

MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "governance_packet_index"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_modify_governance_packets": False,
    "can_modify_index_without_governed_persistence": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "governance_index_awareness_only",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _index_root() -> Path:
    return ensure_dir(get_state_root() / "governance_packet_index")


def _latest_path() -> Path:
    return _index_root() / "latest_index.json"


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_bool(value: Any) -> bool:
    return bool(value is True)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _packet_hash(packet: Dict[str, Any]) -> str:
    integrity = _safe_dict(packet.get("integrity"))
    existing = _safe_str(integrity.get("payload_hash"))
    if existing:
        return existing
    return sha256_text(stable_json_dumps(packet))


def _default_index() -> Dict[str, Any]:
    return {
        "artifact_type": "governance_packet_index",
        "artifact_version": INDEX_VERSION,
        "generated_at": _utc_now_iso(),
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "entries": [],
    }


def _read_index() -> Dict[str, Any]:
    path = _latest_path()
    if not path.exists():
        return _default_index()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_index()

    if not isinstance(payload, dict):
        return _default_index()

    payload.setdefault("entries", [])
    if not isinstance(payload["entries"], list):
        payload["entries"] = []

    payload["artifact_type"] = "governance_packet_index"
    payload["artifact_version"] = INDEX_VERSION
    payload["persistence_type"] = PERSISTENCE_TYPE
    payload["mutation_class"] = MUTATION_CLASS
    payload["advisory_only"] = True
    payload["authority_metadata"] = dict(AUTHORITY_METADATA)

    return payload


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
    normalized = dict(payload)
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)

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

    return governed_write_json(path, normalized)


def build_governance_index_entry(
    *,
    packet: Dict[str, Any],
    packet_path: str,
) -> Dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")

    request = _safe_dict(packet.get("request"))
    execution_gate = _safe_dict(packet.get("execution_gate"))

    return {
        "artifact_type": "governance_packet_index_entry",
        "artifact_version": INDEX_VERSION,
        "indexed_at": _utc_now_iso(),
        "governance_packet_id": _safe_str(packet.get("governance_packet_id")),
        "profile": _safe_str(packet.get("profile")),
        "action": _safe_str(packet.get("action")),
        "status": _safe_str(packet.get("status")),
        "allowed": _safe_bool(packet.get("allowed")),
        "project_id": _safe_str(packet.get("project_id") or request.get("project_id")),
        "phase_id": _safe_str(packet.get("phase_id") or request.get("phase_id")),
        "route": _safe_str(request.get("route")),
        "request_id": _safe_str(request.get("request_id")),
        "execution_gate_allowed": _safe_bool(execution_gate.get("allowed")),
        "created_at": _safe_str(packet.get("created_at") or packet.get("generated_at")),
        "packet_path": _safe_str(packet_path),
        "payload_hash": _packet_hash(packet),
        "persistence_type": "governance_packet_index_entry",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }


def persist_governance_index_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("entry must be a dict")

    index = _read_index()
    entries = _safe_list(index.get("entries"))
    entries.append(dict(entry))

    index["generated_at"] = _utc_now_iso()
    index["entries"] = entries[-1000:]

    result = _governed_write(_latest_path(), index)

    return {
        "status": "indexed",
        "entry_count": len(index["entries"]),
        "path": str(
            result.get("path")
            if isinstance(result, dict) and result.get("path")
            else _latest_path()
        ),
        "entry": entry,
    }


def index_governance_packet(
    *,
    packet: Dict[str, Any],
    packet_path: str,
) -> Dict[str, Any]:
    entry = build_governance_index_entry(packet=packet, packet_path=packet_path)
    return persist_governance_index_entry(entry)


def record_governance_packet_index_entry(
    *,
    packet: Dict[str, Any],
    packet_path: str,
) -> Dict[str, Any]:
    return index_governance_packet(packet=packet, packet_path=packet_path)


def load_governance_index_entries(limit: int = 1000) -> List[Dict[str, Any]]:
    index = _read_index()
    entries = [
        dict(entry)
        for entry in _safe_list(index.get("entries"))
        if isinstance(entry, dict)
    ]
    safe_limit = max(1, min(_safe_int(limit, 1000), 1000))
    return entries[-safe_limit:]


def load_governance_index(limit: int = 1000) -> Dict[str, Any]:
    """
    Backward-compatible read surface expected by governance_index_awareness.

    Read-only. Does not mutate state.
    """
    index = _read_index()
    entries = [
        dict(entry)
        for entry in _safe_list(index.get("entries"))
        if isinstance(entry, dict)
    ]

    safe_limit = max(1, min(_safe_int(limit, 1000), 1000))
    bounded_entries = entries[-safe_limit:]

    return {
        "status": "ok",
        "artifact_type": "governance_packet_index",
        "artifact_version": INDEX_VERSION,
        "generated_at": index.get("generated_at", _utc_now_iso()),
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "entries": bounded_entries,
        "records": bounded_entries,
        "entry_count": len(bounded_entries),
        "total_entry_count": len(entries),
        "source_path": str(_latest_path()),
        "visibility_mode": "read_only",
        "sealed": True,
    }


def _bounded_entries(limit: int = 200) -> List[Dict[str, Any]]:
    safe_limit = max(1, min(_safe_int(limit, 200), 1000))
    return load_governance_index_entries(limit=safe_limit)


def _build_trends(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts: Dict[str, int] = {}
    blocked_paths: Dict[str, int] = {}

    for entry in entries:
        status = _safe_str(entry.get("status")) or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

        if not _safe_bool(entry.get("allowed")):
            route = _safe_str(entry.get("route")) or "unknown"
            blocked_paths[route] = blocked_paths.get(route, 0) + 1

    top_blocked_paths = [
        {"route": route, "count": count}
        for route, count in sorted(
            blocked_paths.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
    ]

    return {
        "entry_count": len(entries),
        "status_counts": status_counts,
        "top_blocked_paths": top_blocked_paths,
    }


def _build_anomaly_flags(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []

    for entry in entries:
        if not _safe_str(entry.get("governance_packet_id")):
            flags.append(
                {
                    "severity": "medium",
                    "code": "missing_governance_packet_id",
                    "route": _safe_str(entry.get("route")),
                    "indexed_at": _safe_str(entry.get("indexed_at")),
                }
            )

        if _safe_bool(entry.get("execution_gate_allowed")) and not _safe_bool(
            entry.get("allowed")
        ):
            flags.append(
                {
                    "severity": "high",
                    "code": "execution_gate_allowed_but_packet_blocked",
                    "route": _safe_str(entry.get("route")),
                    "governance_packet_id": _safe_str(entry.get("governance_packet_id")),
                }
            )

    return flags


def _build_replay_analysis(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    seen: Dict[str, int] = {}

    for entry in entries:
        key = "|".join(
            [
                _safe_str(entry.get("profile")),
                _safe_str(entry.get("action")),
                _safe_str(entry.get("project_id")),
                _safe_str(entry.get("phase_id")),
                _safe_str(entry.get("route")),
            ]
        )
        seen[key] = seen.get(key, 0) + 1

    candidates = [
        {"signature": key, "count": count}
        for key, count in seen.items()
        if count > 1
    ]
    candidates.sort(key=lambda item: item["count"], reverse=True)

    return {
        "candidate_count": len(candidates),
        "candidates": candidates[:25],
    }


def _build_correlations(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_profile: Dict[str, int] = {}
    by_action: Dict[str, int] = {}

    for entry in entries:
        profile = _safe_str(entry.get("profile")) or "unknown"
        action = _safe_str(entry.get("action")) or "unknown"
        by_profile[profile] = by_profile.get(profile, 0) + 1
        by_action[action] = by_action.get(action, 0) + 1

    return {
        "by_profile": by_profile,
        "by_action": by_action,
    }


def _build_temporal_view(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_oldest_first = sorted(
        entries,
        key=lambda item: _safe_str(item.get("created_at") or item.get("indexed_at")),
    )

    if not sorted_oldest_first:
        return {
            "entry_count": 0,
            "first_seen": "",
            "last_seen": "",
            "latest_entries": [],
        }

    latest_entries = [
        {
            "governance_packet_id": _safe_str(entry.get("governance_packet_id")),
            "profile": _safe_str(entry.get("profile")),
            "action": _safe_str(entry.get("action")),
            "status": _safe_str(entry.get("status")),
            "project_id": _safe_str(entry.get("project_id")),
            "phase_id": _safe_str(entry.get("phase_id")),
            "route": _safe_str(entry.get("route")),
        }
        for entry in sorted_oldest_first[-25:]
    ]

    return {
        "entry_count": len(entries),
        "first_seen": _safe_str(
            sorted_oldest_first[0].get("created_at")
            or sorted_oldest_first[0].get("indexed_at")
        ),
        "last_seen": _safe_str(
            sorted_oldest_first[-1].get("created_at")
            or sorted_oldest_first[-1].get("indexed_at")
        ),
        "latest_entries": latest_entries,
    }


def build_governance_index() -> Dict[str, Any]:
    return _read_index()


def build_governance_index_awareness_packet(
    *,
    limit: int = 200,
) -> Dict[str, Any]:
    entries = _bounded_entries(limit)
    anomaly_flags = _build_anomaly_flags(entries)

    severity_rank = {"high": 3, "medium": 2, "low": 1}
    top_severity = "none"
    if anomaly_flags:
        top_severity = max(
            anomaly_flags,
            key=lambda item: severity_rank.get(_safe_str(item.get("severity")), 0),
        ).get("severity", "unknown")

    return {
        "artifact_type": "governance_index_awareness_packet",
        "artifact_version": AWARENESS_VERSION,
        "generated_at": _utc_now_iso(),
        "visibility_mode": "read_only",
        "persistence_type": "governance_index_awareness_packet",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "authority": {
            "can_execute": False,
            "can_mutate_state": False,
            "can_modify_governance_packets": False,
            "can_modify_index": False,
            "packet_remains_truth": True,
            "index_is_awareness_only": True,
        },
        "source": {
            "source_type": "governance_packet_index",
            "window_limit": max(1, min(_safe_int(limit, 200), 1000)),
            "entry_count": len(entries),
        },
        "summary": {
            "system_awareness_status": "warning" if anomaly_flags else "stable",
            "top_severity": top_severity,
            "anomaly_count": len(anomaly_flags),
            "replay_candidate_count": _build_replay_analysis(entries)["candidate_count"],
        },
        "trend_detection": _build_trends(entries),
        "anomaly_detection": {
            "flag_count": len(anomaly_flags),
            "flags": anomaly_flags[:50],
        },
        "cross_run_correlation": _build_correlations(entries),
        "replay_analysis": _build_replay_analysis(entries),
        "temporal_awareness": _build_temporal_view(entries),
    }


def summarize_governance_index_awareness(
    *,
    limit: int = 200,
) -> Dict[str, Any]:
    packet = build_governance_index_awareness_packet(limit=limit)

    return {
        "status": "ok",
        "artifact_type": "governance_index_awareness_summary",
        "artifact_version": AWARENESS_VERSION,
        "generated_at": packet["generated_at"],
        "visibility_mode": "read_only",
        "persistence_type": "governance_index_awareness_summary",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
        "summary": packet["summary"],
        "trend_detection": {
            "entry_count": packet["trend_detection"]["entry_count"],
            "status_counts": packet["trend_detection"]["status_counts"],
            "top_blocked_paths": packet["trend_detection"]["top_blocked_paths"],
        },
        "anomaly_detection": packet["anomaly_detection"],
        "replay_analysis": {
            "candidate_count": packet["replay_analysis"]["candidate_count"],
            "candidates": packet["replay_analysis"]["candidates"][:10],
        },
    }
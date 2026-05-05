from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from AI_GO.core.governance.governance_packet_index import load_governance_index


AWARENESS_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_bool(value: Any) -> bool:
    return bool(value is True)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _parse_time(value: Any) -> datetime:
    raw = _safe_str(value)
    if not raw:
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        clean = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(clean)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def _load_index_entries() -> List[Dict[str, Any]]:
    index = load_governance_index()
    entries_by_id = _safe_dict(index.get("entries_by_id"))

    entries: List[Dict[str, Any]] = []
    for value in entries_by_id.values():
        if isinstance(value, dict):
            entries.append(dict(value))

    entries.sort(
        key=lambda entry: _parse_time(entry.get("created_at")),
        reverse=True,
    )
    return entries


def _bounded_entries(limit: int) -> List[Dict[str, Any]]:
    safe_limit = max(1, min(_safe_int(limit, 200), 1000))
    return _load_index_entries()[:safe_limit]


def _entry_key(entry: Dict[str, Any]) -> str:
    profile = _safe_str(entry.get("profile")) or "unknown_profile"
    action = _safe_str(entry.get("action")) or "unknown_action"
    status = _safe_str(entry.get("status")) or "unknown_status"
    return f"{profile}:{action}:{status}"


def _path_key(entry: Dict[str, Any]) -> str:
    profile = _safe_str(entry.get("profile")) or "unknown_profile"
    action = _safe_str(entry.get("action")) or "unknown_action"
    route = _safe_str(entry.get("route")) or "unknown_route"
    return f"{profile}:{action}:{route}"


def _project_key(entry: Dict[str, Any]) -> str:
    project_id = _safe_str(entry.get("project_id")) or "unknown_project"
    phase_id = _safe_str(entry.get("phase_id")) or "unknown_phase"
    return f"{project_id}:{phase_id}"


def _status_counts(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    counter: Counter[str] = Counter()

    for entry in entries:
        status = _safe_str(entry.get("status")) or "unknown"
        allowed = _safe_bool(entry.get("allowed"))

        if allowed:
            counter["allowed"] += 1
        else:
            counter["blocked_or_not_allowed"] += 1

        counter[f"status:{status}"] += 1

    return dict(counter)


def _top_counts(counter: Counter[str], limit: int = 10) -> List[Dict[str, Any]]:
    return [
        {
            "key": key,
            "count": count,
        }
        for key, count in counter.most_common(limit)
    ]


def _build_trends(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_profile: Counter[str] = Counter()
    by_action: Counter[str] = Counter()
    by_route: Counter[str] = Counter()
    by_status_path: Counter[str] = Counter()
    blocked_by_path: Counter[str] = Counter()

    for entry in entries:
        profile = _safe_str(entry.get("profile")) or "unknown_profile"
        action = _safe_str(entry.get("action")) or "unknown_action"
        route = _safe_str(entry.get("route")) or "unknown_route"

        by_profile[profile] += 1
        by_action[action] += 1
        by_route[route] += 1
        by_status_path[_entry_key(entry)] += 1

        if not _safe_bool(entry.get("allowed")):
            blocked_by_path[_path_key(entry)] += 1

    return {
        "entry_count": len(entries),
        "status_counts": _status_counts(entries),
        "top_profiles": _top_counts(by_profile),
        "top_actions": _top_counts(by_action),
        "top_routes": _top_counts(by_route),
        "top_status_paths": _top_counts(by_status_path),
        "top_blocked_paths": _top_counts(blocked_by_path),
    }


def _flag(
    *,
    flag_id: str,
    severity: str,
    flag_class: str,
    summary: str,
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "flag_id": flag_id,
        "severity": severity,
        "class": flag_class,
        "summary": summary,
        "evidence": evidence or {},
    }


def _build_anomaly_flags(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []

    duplicate_request_counter: Counter[str] = Counter()
    blocked_path_counter: Counter[str] = Counter()

    for entry in entries:
        packet_id = _safe_str(entry.get("governance_packet_id"))
        request_id = _safe_str(entry.get("request_id"))

        if request_id:
            duplicate_request_counter[request_id] += 1

        if not _safe_bool(entry.get("allowed")):
            blocked_path_counter[_path_key(entry)] += 1

        if not packet_id:
            flags.append(
                _flag(
                    flag_id="governance_entry_missing_packet_id",
                    severity="high",
                    flag_class="index_integrity",
                    summary="A governance index entry is missing governance_packet_id.",
                    evidence={"entry": entry},
                )
            )

        if _safe_bool(entry.get("pointer_only")) is not True:
            flags.append(
                _flag(
                    flag_id=f"pointer_only_false:{packet_id or 'unknown'}",
                    severity="high",
                    flag_class="index_integrity",
                    summary="Governance index entry is not pointer-only.",
                    evidence={"governance_packet_id": packet_id},
                )
            )

        if _safe_bool(entry.get("packet_remains_truth")) is not True:
            flags.append(
                _flag(
                    flag_id=f"packet_truth_false:{packet_id or 'unknown'}",
                    severity="high",
                    flag_class="index_integrity",
                    summary="Governance index entry does not preserve packet_remains_truth.",
                    evidence={"governance_packet_id": packet_id},
                )
            )

        allowed = _safe_bool(entry.get("allowed"))
        execution_gate_allowed = _safe_bool(entry.get("execution_gate_allowed"))

        if execution_gate_allowed and not allowed:
            flags.append(
                _flag(
                    flag_id=f"execution_gate_allowed_but_packet_blocked:{packet_id or 'unknown'}",
                    severity="high",
                    flag_class="causality_conflict",
                    summary="Execution gate appears allowed while governance packet is not allowed.",
                    evidence={
                        "governance_packet_id": packet_id,
                        "allowed": allowed,
                        "execution_gate_allowed": execution_gate_allowed,
                    },
                )
            )

    for request_id, count in duplicate_request_counter.items():
        if count > 1:
            flags.append(
                _flag(
                    flag_id=f"duplicate_request_id:{request_id}",
                    severity="medium",
                    flag_class="replay_or_duplicate",
                    summary="Same request_id appears more than once in the governance index window.",
                    evidence={"request_id": request_id, "count": count},
                )
            )

    for path, count in blocked_path_counter.items():
        if count >= 3:
            flags.append(
                _flag(
                    flag_id=f"repeated_blocked_path:{path}",
                    severity="medium",
                    flag_class="repeated_failure",
                    summary="Same governed path has repeated blocked outcomes.",
                    evidence={"path": path, "blocked_count": count},
                )
            )

    return flags


def _build_correlations(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_project: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_request: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_path: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for entry in entries:
        by_project[_project_key(entry)].append(entry)

        request_id = _safe_str(entry.get("request_id"))
        if request_id:
            by_request[request_id].append(entry)

        by_path[_path_key(entry)].append(entry)

    project_sequences: List[Dict[str, Any]] = []
    for key, grouped in by_project.items():
        if len(grouped) < 2:
            continue

        grouped_sorted = sorted(
            grouped,
            key=lambda entry: _parse_time(entry.get("created_at")),
        )

        project_sequences.append(
            {
                "project_phase": key,
                "event_count": len(grouped_sorted),
                "first_seen": _safe_str(grouped_sorted[0].get("created_at")),
                "last_seen": _safe_str(grouped_sorted[-1].get("created_at")),
                "actions": [
                    _safe_str(entry.get("action")) or "unknown_action"
                    for entry in grouped_sorted
                ],
                "statuses": [
                    _safe_str(entry.get("status")) or "unknown_status"
                    for entry in grouped_sorted
                ],
            }
        )

    duplicate_requests = [
        {
            "request_id": request_id,
            "count": len(grouped),
            "packet_ids": [
                _safe_str(entry.get("governance_packet_id"))
                for entry in grouped
            ],
        }
        for request_id, grouped in by_request.items()
        if len(grouped) > 1
    ]

    repeated_paths = [
        {
            "path": path,
            "count": len(grouped),
            "allowed_count": sum(1 for entry in grouped if _safe_bool(entry.get("allowed"))),
            "blocked_count": sum(1 for entry in grouped if not _safe_bool(entry.get("allowed"))),
        }
        for path, grouped in by_path.items()
        if len(grouped) > 1
    ]

    project_sequences.sort(key=lambda item: item["event_count"], reverse=True)
    duplicate_requests.sort(key=lambda item: item["count"], reverse=True)
    repeated_paths.sort(key=lambda item: item["count"], reverse=True)

    return {
        "project_sequences": project_sequences[:20],
        "duplicate_requests": duplicate_requests[:20],
        "repeated_paths": repeated_paths[:20],
    }


def _build_replay_analysis(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    replay_candidates: List[Dict[str, Any]] = []

    grouped: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)

    for entry in entries:
        key = (
            _safe_str(entry.get("project_id")),
            _safe_str(entry.get("phase_id")),
            _safe_str(entry.get("action")),
            _safe_str(entry.get("route")),
        )
        grouped[key].append(entry)

    for key, group in grouped.items():
        if len(group) < 2:
            continue

        statuses = sorted({_safe_str(entry.get("status")) for entry in group})
        allowed_values = sorted({_safe_bool(entry.get("allowed")) for entry in group})

        replay_candidates.append(
            {
                "project_id": key[0],
                "phase_id": key[1],
                "action": key[2],
                "route": key[3],
                "count": len(group),
                "statuses": statuses,
                "allowed_values": allowed_values,
                "packet_ids": [
                    _safe_str(entry.get("governance_packet_id"))
                    for entry in group[:10]
                ],
                "replay_value": "high" if len(statuses) > 1 or len(allowed_values) > 1 else "medium",
            }
        )

    replay_candidates.sort(
        key=lambda item: (item["replay_value"] == "high", item["count"]),
        reverse=True,
    )

    return {
        "candidate_count": len(replay_candidates),
        "candidates": replay_candidates[:25],
    }


def _build_temporal_view(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not entries:
        return {
            "entry_count": 0,
            "first_seen": None,
            "last_seen": None,
            "latest_entries": [],
        }

    sorted_oldest_first = sorted(
        entries,
        key=lambda entry: _parse_time(entry.get("created_at")),
    )

    latest_entries = [
        {
            "governance_packet_id": _safe_str(entry.get("governance_packet_id")),
            "created_at": _safe_str(entry.get("created_at")),
            "profile": _safe_str(entry.get("profile")),
            "action": _safe_str(entry.get("action")),
            "status": _safe_str(entry.get("status")),
            "allowed": _safe_bool(entry.get("allowed")),
            "project_id": _safe_str(entry.get("project_id")),
            "phase_id": _safe_str(entry.get("phase_id")),
            "route": _safe_str(entry.get("route")),
        }
        for entry in entries[:25]
    ]

    return {
        "entry_count": len(entries),
        "first_seen": _safe_str(sorted_oldest_first[0].get("created_at")),
        "last_seen": _safe_str(sorted_oldest_first[-1].get("created_at")),
        "latest_entries": latest_entries,
    }


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
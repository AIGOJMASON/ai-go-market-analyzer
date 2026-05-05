from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from AI_GO.core.memory.memory_integration import load_system_memory_index


PATTERN_RECOGNITION_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(v: Any) -> str:
    return str(v or "").strip()


def _safe_bool(v: Any) -> bool:
    return bool(v is True)


# -------------------------
# Pattern Builders
# -------------------------

def _build_action_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counter = Counter()

    for r in records:
        ctx = r.get("context", {})
        key = (
            _safe_str(ctx.get("action")),
            _safe_str(ctx.get("route")),
        )
        counter[key] += 1

    return [
        {
            "action": k[0],
            "route": k[1],
            "count": v,
        }
        for k, v in counter.most_common(20)
    ]


def _build_failure_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counter = Counter()

    for r in records:
        ctx = r.get("context", {})

        if not _safe_bool(ctx.get("allowed")):
            key = (
                _safe_str(ctx.get("action")),
                _safe_str(ctx.get("route")),
            )
            counter[key] += 1

    return [
        {
            "action": k[0],
            "route": k[1],
            "failure_count": v,
        }
        for k, v in counter.most_common(20)
    ]


def _build_project_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = defaultdict(list)

    for r in records:
        ctx = r.get("context", {})
        key = (
            _safe_str(ctx.get("project_id")),
            _safe_str(ctx.get("phase_id")),
        )
        grouped[key].append(r)

    patterns = []

    for (project_id, phase_id), group in grouped.items():
        allowed = sum(1 for r in group if _safe_bool(r.get("context", {}).get("allowed")))
        blocked = len(group) - allowed

        patterns.append({
            "project_id": project_id,
            "phase_id": phase_id,
            "total_events": len(group),
            "allowed": allowed,
            "blocked": blocked,
        })

    patterns.sort(key=lambda x: x["total_events"], reverse=True)
    return patterns[:20]


def _build_repetition_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counter = Counter()

    for r in records:
        ctx = r.get("context", {})
        request_id = _safe_str(ctx.get("request_id"))

        if request_id:
            counter[request_id] += 1

    return [
        {
            "request_id": req,
            "count": count,
        }
        for req, count in counter.items()
        if count > 1
    ]


# -------------------------
# Signal Builder
# -------------------------

def _build_pattern_signals(
    action_patterns,
    failure_patterns,
    repetition_patterns
) -> Dict[str, Any]:

    signals = []

    if failure_patterns and failure_patterns[0]["failure_count"] >= 3:
        signals.append({
            "type": "repeated_failure_cluster",
            "severity": "medium",
            "evidence": failure_patterns[0],
        })

    if repetition_patterns:
        signals.append({
            "type": "duplicate_request_pattern",
            "severity": "medium",
            "count": len(repetition_patterns),
        })

    if action_patterns and action_patterns[0]["count"] >= 5:
        signals.append({
            "type": "high_frequency_action",
            "severity": "low",
            "evidence": action_patterns[0],
        })

    return {
        "signal_count": len(signals),
        "signals": signals,
    }


# -------------------------
# Public API
# -------------------------

def build_pattern_recognition_packet(limit: int = 500) -> Dict[str, Any]:
    index = load_system_memory_index()
    records = list(index.get("records_by_id", {}).values())[:limit]

    action_patterns = _build_action_patterns(records)
    failure_patterns = _build_failure_patterns(records)
    project_patterns = _build_project_patterns(records)
    repetition_patterns = _build_repetition_patterns(records)

    signals = _build_pattern_signals(
        action_patterns,
        failure_patterns,
        repetition_patterns,
    )

    return {
        "artifact_type": "pattern_recognition_packet",
        "artifact_version": PATTERN_RECOGNITION_VERSION,
        "generated_at": _utc_now_iso(),

        "authority": {
            "read_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_influence_execution": False,
        },

        "summary": {
            "pattern_count": (
                len(action_patterns)
                + len(failure_patterns)
                + len(project_patterns)
            ),
            "signal_count": signals["signal_count"],
        },

        "patterns": {
            "action_patterns": action_patterns,
            "failure_patterns": failure_patterns,
            "project_patterns": project_patterns,
            "repetition_patterns": repetition_patterns,
        },

        "pattern_signals": signals,
    }
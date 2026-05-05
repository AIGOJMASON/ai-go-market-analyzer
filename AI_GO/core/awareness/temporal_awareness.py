from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from AI_GO.core.memory.memory_integration import load_system_memory_index


TEMPORAL_AWARENESS_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(v: Any) -> str:
    return str(v or "").strip()


def _safe_bool(v: Any) -> bool:
    return bool(v is True)


def _parse_time(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


# -------------------------
# Core Sequencing
# -------------------------

def _group_by_project_phase(records: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
    grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    for r in records:
        ctx = r.get("context", {})
        key = (
            _safe_str(ctx.get("project_id")),
            _safe_str(ctx.get("phase_id")),
        )

        grouped.setdefault(key, []).append(r)

    return grouped


def _sort_sequence(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(records, key=lambda r: _parse_time(_safe_str(r.get("created_at"))))


# -------------------------
# Sequence Classification
# -------------------------

def _classify_sequence(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"type": "empty"}

    statuses = []
    allowed_flags = []

    for r in records:
        ctx = r.get("context", {})
        statuses.append(_safe_str(ctx.get("status")))
        allowed_flags.append(_safe_bool(ctx.get("allowed")))

    transitions = []
    for i in range(1, len(statuses)):
        transitions.append((statuses[i - 1], statuses[i]))

    allowed_count = sum(1 for a in allowed_flags if a)
    blocked_count = len(allowed_flags) - allowed_count

    if blocked_count == 0:
        seq_type = "stable_success"
    elif allowed_count == 0:
        seq_type = "stable_failure"
    elif transitions and any(prev == "blocked" and curr == "allowed" for prev, curr in transitions):
        seq_type = "recovery_path"
    elif transitions and any(prev == "allowed" and curr == "blocked" for prev, curr in transitions):
        seq_type = "degradation_path"
    else:
        seq_type = "mixed"

    return {
        "type": seq_type,
        "event_count": len(records),
        "allowed_count": allowed_count,
        "blocked_count": blocked_count,
        "transitions": transitions[:20],
    }


# -------------------------
# Sequence Builder
# -------------------------

def _build_sequences(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = _group_by_project_phase(records)

    sequences: List[Dict[str, Any]] = []

    for (project_id, phase_id), group in grouped.items():
        ordered = _sort_sequence(group)

        classification = _classify_sequence(ordered)

        sequences.append({
            "project_id": project_id,
            "phase_id": phase_id,
            "sequence_length": len(ordered),
            "first_event": ordered[0]["created_at"],
            "last_event": ordered[-1]["created_at"],
            "classification": classification,
            "actions": [
                _safe_str(r.get("context", {}).get("action"))
                for r in ordered
            ],
            "statuses": [
                _safe_str(r.get("context", {}).get("status"))
                for r in ordered
            ],
        })

    sequences.sort(key=lambda s: s["sequence_length"], reverse=True)

    return sequences[:50]


# -------------------------
# Temporal Signals
# -------------------------

def _build_temporal_signals(sequences: List[Dict[str, Any]]) -> Dict[str, Any]:
    signal_counts = {
        "stable_success": 0,
        "stable_failure": 0,
        "recovery_path": 0,
        "degradation_path": 0,
        "mixed": 0,
    }

    for seq in sequences:
        t = seq["classification"]["type"]
        if t in signal_counts:
            signal_counts[t] += 1

    dominant = max(signal_counts.items(), key=lambda x: x[1])[0] if sequences else "none"

    return {
        "signal_counts": signal_counts,
        "dominant_pattern": dominant,
        "sequence_count": len(sequences),
    }


# -------------------------
# Public API
# -------------------------

def build_temporal_awareness_packet(limit: int = 500) -> Dict[str, Any]:
    index = load_system_memory_index()
    records_by_id = index.get("records_by_id", {})

    records = list(records_by_id.values())[:limit]

    sequences = _build_sequences(records)
    signals = _build_temporal_signals(sequences)

    return {
        "artifact_type": "temporal_awareness_packet",
        "artifact_version": TEMPORAL_AWARENESS_VERSION,
        "generated_at": _utc_now_iso(),

        "authority": {
            "read_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_influence_execution": False,
        },

        "summary": {
            "sequence_count": len(sequences),
            "dominant_pattern": signals["dominant_pattern"],
        },

        "temporal_sequences": sequences,
        "temporal_signals": signals,
    }
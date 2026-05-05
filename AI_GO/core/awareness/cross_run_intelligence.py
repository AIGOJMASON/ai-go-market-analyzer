from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.awareness.unified_system_awareness import (
    build_unified_system_awareness_packet,
)
from AI_GO.core.governance.governed_persistence import (
    build_authority_metadata,
    governed_append_jsonl,
)
from AI_GO.core.paths.path_resolver import ensure_dir, ensure_parent, get_state_root


CROSS_RUN_INTELLIGENCE_VERSION = "v1.1"
CROSS_RUN_MUTATION_CLASS = "cross_run_awareness_history_persistence"
CROSS_RUN_PERSISTENCE_TYPE = "unified_awareness_history_jsonl"
CROSS_RUN_ADVISORY_ONLY = True


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _awareness_root() -> Path:
    return ensure_dir(get_state_root() / "system_awareness")


def _history_path() -> Path:
    return ensure_parent(_awareness_root() / "unified_awareness_history.jsonl")


def _parse_time(value: Any) -> datetime:
    raw = _safe_str(value)
    if not raw:
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def _unwrap_history_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if payload.get("artifact_type") == "governed_jsonl_record":
        inner = payload.get("payload", {})
        return inner if isinstance(inner, dict) else {}
    return payload


def _load_history() -> List[Dict[str, Any]]:
    path = _history_path()
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean:
            continue

        try:
            payload = json.loads(clean)
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            unwrapped = _unwrap_history_payload(payload)
            if unwrapped:
                records.append(unwrapped)

    records.sort(key=lambda item: _parse_time(item.get("generated_at")))
    return records


def _build_history_record(packet: Dict[str, Any], run_id: str = "") -> Dict[str, Any]:
    summary = _safe_dict(packet.get("summary"))

    return {
        "artifact_type": "unified_awareness_history_record",
        "artifact_version": CROSS_RUN_INTELLIGENCE_VERSION,
        "recorded_at": _utc_now_iso(),
        "generated_at": _safe_str(packet.get("generated_at")),
        "run_id": _safe_str(run_id) or f"awareness-run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "source_artifact_type": _safe_str(packet.get("artifact_type")),
        "source_artifact_version": _safe_str(packet.get("artifact_version")),
        "summary": {
            "system_posture": _safe_str(summary.get("system_posture")),
            "conditioned_risk_posture": _safe_str(summary.get("conditioned_risk_posture")),
            "escalation_hint": _safe_str(summary.get("escalation_hint")),
            "anomaly_count": _safe_int(summary.get("anomaly_count")),
            "memory_record_count": _safe_int(summary.get("memory_record_count")),
            "sequence_count": _safe_int(summary.get("sequence_count")),
            "pattern_signal_count": _safe_int(summary.get("pattern_signal_count")),
        },
        "classification": {
            "mutation_class": CROSS_RUN_MUTATION_CLASS,
            "persistence_type": CROSS_RUN_PERSISTENCE_TYPE,
            "advisory_only": CROSS_RUN_ADVISORY_ONLY,
            "execution_allowed": False,
            "runtime_mutation_allowed": False,
            "recommendation_mutation_allowed": False,
            "pm_authority_mutation_allowed": False,
        },
        "authority": {
            "visibility_artifact_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_operational_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
        },
        "sealed": True,
    }


def _authority_metadata(path: Path, run_id: str) -> Dict[str, Any]:
    return build_authority_metadata(
        authority_id="core_awareness_cross_run_intelligence",
        operation="append_unified_awareness_history_record",
        actor="system",
        source="AI_GO.core.awareness.cross_run_intelligence",
        extra={
            "target_path": str(path),
            "run_id": run_id,
            "advisory_only": CROSS_RUN_ADVISORY_ONLY,
        },
    )


def append_unified_awareness_history_record(
    *,
    run_id: str = "",
    limit: int = 500,
) -> Dict[str, Any]:
    packet = build_unified_system_awareness_packet(limit=limit)
    record = _build_history_record(packet, run_id=run_id)

    path = _history_path()
    mutation_class = CROSS_RUN_MUTATION_CLASS
    persistence_type = CROSS_RUN_PERSISTENCE_TYPE
    advisory_only = CROSS_RUN_ADVISORY_ONLY
    authority_metadata = _authority_metadata(path, _safe_str(record.get("run_id")))

    governed_append_jsonl(
        path=path,
        record=record,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        advisory_only=advisory_only,
    )

    return {
        "status": "recorded",
        "artifact_type": "unified_awareness_history_write",
        "artifact_version": CROSS_RUN_INTELLIGENCE_VERSION,
        "path": str(path),
        "record": record,
        "authority": record["authority"],
        "classification": record["classification"],
        "authority_metadata": authority_metadata,
    }


def _posture_rank(posture: str) -> int:
    normalized = _safe_str(posture)

    ranks = {
        "limited_data": 0,
        "aware": 1,
        "neutral": 1,
        "cautious": 2,
        "high_caution": 3,
    }

    return ranks.get(normalized, 1)


def _trend_from_values(values: List[int]) -> str:
    if len(values) < 2:
        return "insufficient_history"

    first = values[0]
    last = values[-1]

    if last > first:
        return "worsening"

    if last < first:
        return "improving"

    if len(set(values)) > 2:
        return "volatile"

    return "stable"


def _delta(first: int, last: int) -> int:
    return last - first


def _build_trajectory(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    points: List[Dict[str, Any]] = []

    for record in records:
        summary = _safe_dict(record.get("summary"))
        posture = _safe_str(summary.get("system_posture")) or "unknown"

        points.append(
            {
                "run_id": _safe_str(record.get("run_id")),
                "generated_at": _safe_str(record.get("generated_at")),
                "recorded_at": _safe_str(record.get("recorded_at")),
                "system_posture": posture,
                "system_posture_rank": _posture_rank(posture),
                "conditioned_risk_posture": _safe_str(summary.get("conditioned_risk_posture")),
                "anomaly_count": _safe_int(summary.get("anomaly_count")),
                "memory_record_count": _safe_int(summary.get("memory_record_count")),
                "sequence_count": _safe_int(summary.get("sequence_count")),
                "pattern_signal_count": _safe_int(summary.get("pattern_signal_count")),
            }
        )

    return {
        "point_count": len(points),
        "points": points[-50:],
    }


def _build_drift_detection(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(records) < 2:
        return {
            "status": "insufficient_history",
            "drift": "unknown",
            "signals": [],
        }

    summaries = [_safe_dict(record.get("summary")) for record in records]

    posture_values = [
        _posture_rank(_safe_str(summary.get("system_posture")))
        for summary in summaries
    ]
    anomaly_values = [
        _safe_int(summary.get("anomaly_count"))
        for summary in summaries
    ]
    pattern_values = [
        _safe_int(summary.get("pattern_signal_count"))
        for summary in summaries
    ]

    signals: List[Dict[str, Any]] = []

    posture_trend = _trend_from_values(posture_values)
    anomaly_delta = _delta(anomaly_values[0], anomaly_values[-1])
    pattern_delta = _delta(pattern_values[0], pattern_values[-1])

    if posture_trend == "worsening":
        signals.append(
            {
                "signal_type": "posture_worsening",
                "severity": "medium",
                "summary": "System posture increased in caution across recorded runs.",
            }
        )

    if posture_trend == "improving":
        signals.append(
            {
                "signal_type": "posture_improving",
                "severity": "low",
                "summary": "System posture relaxed across recorded runs.",
            }
        )

    if anomaly_delta > 0:
        signals.append(
            {
                "signal_type": "anomaly_count_rising",
                "severity": "medium",
                "delta": anomaly_delta,
                "summary": "Anomaly count increased across recorded runs.",
            }
        )

    if pattern_delta > 0:
        signals.append(
            {
                "signal_type": "pattern_signal_rising",
                "severity": "medium",
                "delta": pattern_delta,
                "summary": "Pattern signal count increased across recorded runs.",
            }
        )

    if posture_trend == "volatile":
        signals.append(
            {
                "signal_type": "posture_volatility",
                "severity": "medium",
                "summary": "System posture oscillated across recorded runs.",
            }
        )

    if not signals:
        drift = "stable"
    elif any(signal.get("signal_type", "").endswith("rising") for signal in signals):
        drift = "worsening"
    elif posture_trend == "improving":
        drift = "improving"
    elif posture_trend == "volatile":
        drift = "volatile"
    else:
        drift = posture_trend

    return {
        "status": "ok",
        "drift": drift,
        "posture_trend": posture_trend,
        "anomaly_delta": anomaly_delta,
        "pattern_signal_delta": pattern_delta,
        "signals": signals,
    }


def _build_persistence_detection(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    posture_counter: Counter[str] = Counter()
    risk_counter: Counter[str] = Counter()

    for record in records:
        summary = _safe_dict(record.get("summary"))
        posture_counter[_safe_str(summary.get("system_posture")) or "unknown"] += 1
        risk_counter[_safe_str(summary.get("conditioned_risk_posture")) or "unknown"] += 1

    persistent_signals: List[Dict[str, Any]] = []

    if posture_counter:
        posture, count = posture_counter.most_common(1)[0]
        if count >= 3:
            persistent_signals.append(
                {
                    "signal_type": "persistent_system_posture",
                    "posture": posture,
                    "count": count,
                    "summary": "Same system posture persisted across multiple awareness runs.",
                }
            )

    if risk_counter:
        risk_posture, count = risk_counter.most_common(1)[0]
        if count >= 3:
            persistent_signals.append(
                {
                    "signal_type": "persistent_risk_posture",
                    "risk_posture": risk_posture,
                    "count": count,
                    "summary": "Same conditioned risk posture persisted across multiple awareness runs.",
                }
            )

    return {
        "posture_counts": dict(posture_counter),
        "risk_posture_counts": dict(risk_counter),
        "persistent_signal_count": len(persistent_signals),
        "persistent_signals": persistent_signals,
    }


def _build_cross_run_summary(
    *,
    history: List[Dict[str, Any]],
    drift: Dict[str, Any],
    persistence: Dict[str, Any],
) -> Dict[str, Any]:
    if not history:
        cross_run_posture = "no_history"
    elif drift.get("drift") == "worsening":
        cross_run_posture = "watch_closely"
    elif drift.get("drift") == "volatile":
        cross_run_posture = "unstable"
    elif persistence.get("persistent_signal_count", 0) > 0:
        cross_run_posture = "persistent_pattern"
    else:
        cross_run_posture = "stable"

    return {
        "cross_run_posture": cross_run_posture,
        "history_count": len(history),
        "drift": drift.get("drift", "unknown"),
        "persistent_signal_count": persistence.get("persistent_signal_count", 0),
    }


def build_cross_run_intelligence_packet(
    *,
    limit: int = 100,
) -> Dict[str, Any]:
    safe_limit = max(1, min(_safe_int(limit, 100), 1000))
    history = _load_history()[-safe_limit:]

    trajectory = _build_trajectory(history)
    drift = _build_drift_detection(history)
    persistence = _build_persistence_detection(history)
    summary = _build_cross_run_summary(
        history=history,
        drift=drift,
        persistence=persistence,
    )

    return {
        "artifact_type": "cross_run_intelligence_packet",
        "artifact_version": CROSS_RUN_INTELLIGENCE_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "read_only_cross_run_stitching",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_operational_state": False,
            "can_override_governance": False,
            "can_override_watcher": False,
            "can_override_execution_gate": False,
            "can_auto_escalate": False,
            "can_auto_condition_pm": False,
        },
        "source": {
            "history_path": str(_history_path()),
            "history_window_limit": safe_limit,
            "history_count": len(history),
        },
        "summary": summary,
        "trajectory": trajectory,
        "drift_detection": drift,
        "persistence_detection": persistence,
        "use_policy": {
            "operator_may_read": True,
            "pm_may_read": True,
            "ai_may_read_later": True,
            "may_support_operator_surface": True,
            "may_support_replay_analysis": True,
            "may_change_execution_gate": False,
            "may_change_watcher": False,
            "may_change_state": False,
            "may_write_decisions": False,
            "may_dispatch_actions": False,
        },
        "sealed": True,
    }


def summarize_cross_run_intelligence(limit: int = 100) -> Dict[str, Any]:
    packet = build_cross_run_intelligence_packet(limit=limit)

    return {
        "status": "ok",
        "artifact_type": "cross_run_intelligence_summary",
        "artifact_version": CROSS_RUN_INTELLIGENCE_VERSION,
        "generated_at": packet["generated_at"],
        "mode": packet["mode"],
        "authority": packet["authority"],
        "summary": packet["summary"],
    }
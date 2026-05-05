from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "state" / "continuity_weighting" / "current" / "continuity_weighting_record.json"
OUTPUT_PATH = PROJECT_ROOT / "state" / "refinement" / "current" / "continuity_weighting_refinement_packet.json"

MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE = "continuity_weighting_refinement_packet"


AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_runtime": False,
    "can_mutate_workflow_state": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "refinement_awareness_only",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        return default

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return default


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return dict(AUTHORITY_METADATA)


def _normalize_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(packet)
    normalized["artifact_type"] = "continuity_weighting_refinement_packet"
    normalized["artifact_version"] = "northstar_refinement_bridge_v1"
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["annotation_only"] = True
    normalized["classification"] = _classification_block()
    normalized["authority"] = _authority_block()
    normalized["sealed"] = True
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> str:
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
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _default_weighting_record() -> Dict[str, Any]:
    return {
        "record_id": "continuity_weighting_default",
        "timestamp": None,
        "ranked_patterns": [],
        "summary": {},
    }


def _classify_confidence_posture(weight: float) -> str:
    if weight >= 1.0:
        return "strong_attention"
    if weight >= 0.75:
        return "elevated_attention"
    if weight >= 0.50:
        return "slight_attention"
    return "none"


def _classify_signal_class(weight: float) -> str:
    if weight >= 1.0:
        return "dominant_pattern"
    if weight >= 0.75:
        return "active_pattern"
    if weight >= 0.50:
        return "emerging_pattern"
    return "low_signal"


def _build_advisory_note(
    continuity_key: Optional[str],
    pattern_status: Optional[str],
    recurrence_count: int,
    event_theme: Optional[str],
    symbol: Optional[str],
) -> str:
    parts: list[str] = []

    if continuity_key:
        parts.append(f"Pattern {continuity_key} is currently {pattern_status or 'observed'}")
    else:
        parts.append("No continuity pattern available")

    if recurrence_count > 0:
        parts.append(f"with recurrence count {recurrence_count}")

    if event_theme:
        parts.append(f"theme={event_theme}")

    if symbol:
        parts.append(f"symbol={symbol}")

    return "; ".join(parts)


def build_continuity_weighting_refinement_packet() -> Dict[str, Any]:
    weighting_record = _read_json(INPUT_PATH, _default_weighting_record())

    ranked_patterns = weighting_record.get("ranked_patterns")
    if not isinstance(ranked_patterns, list):
        ranked_patterns = []

    top_pattern = ranked_patterns[0] if ranked_patterns else {}
    if not isinstance(top_pattern, dict):
        top_pattern = {}

    try:
        weight = float(top_pattern.get("weight", 0.0) or 0.0)
    except Exception:
        weight = 0.0

    recurrence_count = int(top_pattern.get("recurrence_count", 0) or 0)
    continuity_key = top_pattern.get("continuity_key")
    pattern_status = top_pattern.get("pattern_status")
    event_theme = top_pattern.get("event_theme")
    symbol = top_pattern.get("symbol")

    packet = {
        "packet_id": f"continuity_weighting_refinement_{utc_now_iso().replace(':', '-')}",
        "timestamp": utc_now_iso(),
        "source_record_path": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "source_record_id": weighting_record.get("record_id"),
        "annotation_only": True,
        "source_surface": top_pattern.get("source_surface"),
        "top_pattern_key": continuity_key,
        "top_pattern_status": pattern_status,
        "top_pattern_weight": weight,
        "recurrence_count": recurrence_count,
        "event_class": top_pattern.get("event_class"),
        "symbol": symbol,
        "event_theme": event_theme,
        "signal_class": _classify_signal_class(weight),
        "confidence_posture": _classify_confidence_posture(weight),
        "advisory_note": _build_advisory_note(
            continuity_key=continuity_key,
            pattern_status=pattern_status,
            recurrence_count=recurrence_count,
            event_theme=event_theme,
            symbol=symbol,
        ),
    }

    return _normalize_packet(packet)


def generate_and_persist_continuity_weighting_refinement_packet() -> Dict[str, Any]:
    packet = build_continuity_weighting_refinement_packet()
    packet["path"] = _governed_write(OUTPUT_PATH, packet)
    return packet
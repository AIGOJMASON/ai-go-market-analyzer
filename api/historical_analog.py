from collections import Counter
from typing import Any, Dict, List, Set

from AI_GO.api.historical_analog_library import get_historical_analog_library


REQUIRED_CLASSIFICATION_KEYS = {
    "event_theme",
    "classification_confidence",
    "signals",
}

REQUIRED_SIGNAL_STACK_KEYS = {
    "artifact_type",
    "sealed",
    "stack_signals",
    "stack_summary",
}


def _validate_classification_panel(classification_panel: Dict[str, Any]) -> None:
    if not isinstance(classification_panel, dict):
        raise ValueError("classification_panel must be a dict")

    missing = REQUIRED_CLASSIFICATION_KEYS.difference(classification_panel.keys())
    if missing:
        raise ValueError(f"classification_panel missing required keys: {sorted(missing)}")

    if not isinstance(classification_panel.get("signals"), list):
        raise ValueError("classification_panel signals must be a list")


def _validate_signal_stack_record(signal_stack_record: Dict[str, Any]) -> None:
    if not isinstance(signal_stack_record, dict):
        raise ValueError("signal_stack_record must be a dict")

    missing = REQUIRED_SIGNAL_STACK_KEYS.difference(signal_stack_record.keys())
    if missing:
        raise ValueError(f"signal_stack_record missing required keys: {sorted(missing)}")

    if signal_stack_record.get("artifact_type") != "signal_stack_record":
        raise ValueError("signal_stack_record artifact_type must be signal_stack_record")

    if signal_stack_record.get("sealed") is not True:
        raise ValueError("signal_stack_record must be sealed")

    if not isinstance(signal_stack_record.get("stack_signals"), list):
        raise ValueError("signal_stack_record stack_signals must be a list")

    if not isinstance(signal_stack_record.get("stack_summary"), dict):
        raise ValueError("signal_stack_record stack_summary must be a dict")


def _normalize_signals(signals: List[str]) -> Set[str]:
    return {str(item).strip() for item in signals if str(item).strip()}


def _resolve_legality_signal(stack_signals: Set[str]) -> str:
    for signal in stack_signals:
        if signal.startswith("legality:"):
            return signal
    return "legality:unknown"


def _resolve_confirmation_signal(stack_signals: Set[str]) -> str:
    for signal in stack_signals:
        if signal.startswith("confirmation:"):
            return signal
    return "confirmation:unknown"


def _score_analog(
    classification_panel: Dict[str, Any],
    stack_signals: Set[str],
    analog: Dict[str, Any],
) -> Dict[str, Any]:
    score = 0
    matched_signals: List[str] = []

    analog_event_theme = analog.get("event_theme")
    current_event_theme = classification_panel.get("event_theme")
    if analog_event_theme == current_event_theme:
        score += 3

    analog_required_signals = _normalize_signals(analog.get("required_signals", []))
    signal_overlap = sorted(stack_signals.intersection(analog_required_signals))
    matched_signals.extend(signal_overlap)
    score += len(signal_overlap)

    current_legality = _resolve_legality_signal(stack_signals)
    current_confirmation = _resolve_confirmation_signal(stack_signals)

    if current_legality in analog_required_signals:
        score += 1

    if current_confirmation in analog_required_signals:
        score += 1

    return {
        "analog_id": analog["analog_id"],
        "score": score,
        "matched_signals": matched_signals,
        "event_theme": analog["event_theme"],
        "common_pattern": analog["common_pattern"],
        "failure_mode": analog["failure_mode"],
        "confidence_band": analog["confidence_band"],
        "pattern_notes": analog.get("pattern_notes", []),
    }


def _resolve_confidence_band(selected_matches: List[Dict[str, Any]]) -> str:
    if not selected_matches:
        return "low"

    top_score = selected_matches[0]["score"]
    if top_score >= 7:
        return "high"
    if top_score >= 4:
        return "medium"
    return "low"


def _resolve_common_pattern(selected_matches: List[Dict[str, Any]]) -> str:
    if not selected_matches:
        return "No analog pattern cleared the minimum deterministic match threshold."

    counter = Counter(match["common_pattern"] for match in selected_matches)
    return counter.most_common(1)[0][0]


def _resolve_failure_mode(selected_matches: List[Dict[str, Any]]) -> str:
    if not selected_matches:
        return "Insufficient analog strength. Remain bounded and rely on explicit confirmation."

    counter = Counter(match["failure_mode"] for match in selected_matches)
    return counter.most_common(1)[0][0]


def build_historical_analog_record(
    classification_panel: Dict[str, Any],
    signal_stack_record: Dict[str, Any],
    *,
    max_analogs: int = 3,
    min_score: int = 3,
) -> Dict[str, Any]:
    _validate_classification_panel(classification_panel)
    _validate_signal_stack_record(signal_stack_record)

    stack_signals = _normalize_signals(signal_stack_record.get("stack_signals", []))
    library = get_historical_analog_library()

    scored_matches = [
        _score_analog(classification_panel, stack_signals, analog)
        for analog in library
    ]
    scored_matches.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_signals"]),
            item["analog_id"],
        ),
        reverse=True,
    )

    selected_matches = [
        match for match in scored_matches if match["score"] >= min_score
    ][:max_analogs]

    record = {
        "artifact_type": "historical_analog_record",
        "artifact_class": "bounded_read_only_context",
        "sealed": True,
        "event_theme": classification_panel["event_theme"],
        "analog_count": len(selected_matches),
        "common_pattern": _resolve_common_pattern(selected_matches),
        "failure_mode": _resolve_failure_mode(selected_matches),
        "confidence_band": _resolve_confidence_band(selected_matches),
        "matched_signal_count": len(
            {signal for match in selected_matches for signal in match["matched_signals"]}
        ),
        "analogs": [
            {
                "analog_id": match["analog_id"],
                "score": match["score"],
                "matched_signals": match["matched_signals"],
                "common_pattern": match["common_pattern"],
                "failure_mode": match["failure_mode"],
                "confidence_band": match["confidence_band"],
                "pattern_notes": match["pattern_notes"],
            }
            for match in selected_matches
        ],
        "notes": (
            "Deterministic analog comparison only. "
            "No prediction, no recommendation mutation, no side effects."
        ),
        "source_lineage": {
            "classification_artifact": "classification_panel",
            "signal_stack_artifact": signal_stack_record["artifact_type"],
        },
    }
    return record
from __future__ import annotations

from typing import Any, Dict, List


class LiveDataAdapterError(ValueError):
    pass


def _require(mapping: Dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise LiveDataAdapterError(f"Missing required field: {key}")
    return mapping[key]


def normalize_live_input(raw_case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = _require(raw_case, "case_id")
    observed_at = _require(raw_case, "observed_at")
    event_signal = _require(raw_case, "event_signal")
    candidates = _require(raw_case, "candidates")
    macro_context = raw_case.get("macro_context", {})
    operator_notes = raw_case.get("operator_notes", "")

    if not isinstance(event_signal, dict):
        raise LiveDataAdapterError("event_signal must be an object")

    if not isinstance(macro_context, dict):
        macro_context = {}

    confirmed = bool(_require(event_signal, "confirmed"))
    event_theme = _require(event_signal, "event_theme")
    propagation = _require(event_signal, "propagation")

    if not isinstance(candidates, list) or not candidates:
        raise LiveDataAdapterError("At least one candidate is required.")

    normalized_candidates: List[Dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise LiveDataAdapterError(f"Candidate at position {index} must be an object")

        symbol = _require(candidate, "symbol")
        sector = _require(candidate, "sector")
        necessity_qualified = bool(_require(candidate, "necessity_qualified"))
        rebound_confirmed = bool(_require(candidate, "rebound_confirmed"))

        normalized_candidates.append(
            {
                "candidate_id": f"{case_id}-C{index:02d}",
                "symbol": symbol,
                "sector": sector,
                "necessity_qualified": necessity_qualified,
                "rebound_confirmed": rebound_confirmed,
                "entry_signal": candidate.get("entry_signal", "unspecified"),
                "exit_signal": candidate.get("exit_signal", "unspecified"),
                "confidence": candidate.get("confidence", "unknown"),
            }
        )

    return {
        "case_id": case_id,
        "observed_at": observed_at,
        "source_mode": "live_style",
        "event_signal": {
            "confirmed": confirmed,
            "event_theme": event_theme,
            "propagation": propagation,
        },
        "macro_context": {
            "headline": macro_context.get("headline", ""),
            "macro_bias": macro_context.get("macro_bias", "neutral"),
        },
        "candidates": normalized_candidates,
        "operator_notes": operator_notes,
        "governance_defaults": {
            "execution_block_required": True,
            "approval_required": True,
            "execution_allowed": False,
        },
    }
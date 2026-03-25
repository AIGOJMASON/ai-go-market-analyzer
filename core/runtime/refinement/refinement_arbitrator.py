from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.runtime.refinement.refinement_packet_builder import (
    build_refinement_arbitrator_packet,
)


class RefinementArbitratorError(ValueError):
    pass


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _summarize_reasoning(
    *,
    analog_count: int,
    analog_confidence: str,
    quarantine_count: int,
) -> str:
    if analog_count == 0 and quarantine_count == 0:
        return "No material refinement signal was found in analog or quarantine memory."

    if quarantine_count > 0 and analog_confidence in {"medium", "high"}:
        return (
            f"Historical analog support is present, but prior quarantined outcomes "
            f"indicate the shape requires caution."
        )

    if analog_confidence == "high":
        return "Historical analog support is strong and structurally relevant."

    if analog_confidence == "medium":
        return "Historical analog support is present but not decisive."

    return "Historical analog support is weak and should not materially influence interpretation."


def _summarize_narrative(
    *,
    event_theme: str,
    analog_confidence: str,
    risk_flags: List[str],
) -> str:
    if "early_reversal_likelihood" in risk_flags:
        return (
            f"{event_theme} resembles prior cases that looked promising early "
            f"but often reversed before strengthening."
        )

    if analog_confidence == "high":
        return f"{event_theme} has strong historical resemblance, but remains advisory only."

    if analog_confidence == "medium":
        return f"{event_theme} has some historical support, but the pattern is not fully settled."

    return f"{event_theme} does not yet have enough historical support to justify a stronger read."


def _resolve_confidence_adjustment(
    *,
    analog_confidence: str,
    quarantine_count: int,
    watcher_passed: bool,
) -> str:
    if not watcher_passed:
        return "down"

    if quarantine_count > 0:
        return "down"

    if analog_confidence == "high":
        return "up"

    return "none"


def _resolve_risk_flags(
    *,
    analog_panel: Dict[str, Any],
    quarantine_count: int,
    watcher_passed: bool,
) -> List[str]:
    risk_flags: List[str] = []

    common_pattern = str(analog_panel.get("common_pattern", "")).lower()
    failure_mode = str(analog_panel.get("failure_mode", "")).lower()

    if "reverse" in failure_mode or "reversal" in failure_mode:
        risk_flags.append("early_reversal_likelihood")

    if "confirmation" in failure_mode:
        risk_flags.append("weak_confirmation_history")

    if quarantine_count > 0:
        risk_flags.append("failure_cluster_detected")

    if not watcher_passed:
        risk_flags.append("watcher_failure_present")

    if not risk_flags:
        risk_flags.append("no_material_refinement_signal")

    return risk_flags


def build_refinement_arbitrator_packet_from_runtime(
    *,
    core_id: str,
    market_panel: Dict[str, Any],
    historical_analog_panel: Dict[str, Any],
    governance_panel: Dict[str, Any],
    quarantine_items: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    market_panel = _safe_dict(market_panel)
    historical_analog_panel = _safe_dict(historical_analog_panel)
    governance_panel = _safe_dict(governance_panel)
    quarantine_items = _safe_list(quarantine_items)

    event_theme = str(market_panel.get("event_theme", "unknown"))
    analog_count = int(historical_analog_panel.get("analog_count", 0))
    analog_confidence = str(historical_analog_panel.get("confidence_band", "low"))
    watcher_passed = bool(governance_panel.get("watcher_passed", False))
    quarantine_count = len(quarantine_items)

    risk_flags = _resolve_risk_flags(
        analog_panel=historical_analog_panel,
        quarantine_count=quarantine_count,
        watcher_passed=watcher_passed,
    )

    confidence_adjustment = _resolve_confidence_adjustment(
        analog_confidence=analog_confidence,
        quarantine_count=quarantine_count,
        watcher_passed=watcher_passed,
    )

    reasoning_summary = _summarize_reasoning(
        analog_count=analog_count,
        analog_confidence=analog_confidence,
        quarantine_count=quarantine_count,
    )

    narrative_summary = _summarize_narrative(
        event_theme=event_theme,
        analog_confidence=analog_confidence,
        risk_flags=risk_flags,
    )

    refinement_mode = (
        "confidence_conditioning"
        if confidence_adjustment in {"up", "down"}
        else "annotation_only"
    )

    return build_refinement_arbitrator_packet(
        core_id=core_id,
        refinement_mode=refinement_mode,
        confidence_adjustment=confidence_adjustment,
        risk_flags=risk_flags,
        reasoning_summary=reasoning_summary,
        narrative_summary=narrative_summary,
        analog_signal=str(historical_analog_panel.get("common_pattern") or ""),
        historical_failure_bias="present" if quarantine_count > 0 else "absent",
        historical_success_bias="present" if watcher_passed else "absent",
        notes=[
            "Stage 16 arbitrator packet is annotation-only unless explicitly consumed downstream.",
            "No recommendation mutation occurred.",
        ],
        source_lineage={
            "market_panel": "runtime_market_panel",
            "historical_analog_panel": "historical_analog_panel",
            "governance_panel": "governance_panel",
            "quarantine_items_count": quarantine_count,
        },
    )
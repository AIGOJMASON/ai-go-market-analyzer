from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class OutcomeInterpretation:
    event_count: int
    outcome_count: int
    follow_through_count: int
    failure_count: int
    stall_count: int
    follow_through_rate_pct: float
    failure_rate_pct: float
    stall_rate_pct: float
    edge_class: str
    operator_meaning: str
    why_user_should_care: str
    confidence_note: str


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _round_pct(value: float) -> float:
    return round(value, 2)


def _derive_rates_from_counts(
    follow_through_count: int,
    failure_count: int,
    stall_count: int,
    outcome_count: int,
) -> Dict[str, float]:
    if outcome_count <= 0:
        return {
            "follow_through_rate_pct": 0.0,
            "failure_rate_pct": 0.0,
            "stall_rate_pct": 0.0,
        }

    return {
        "follow_through_rate_pct": _round_pct((follow_through_count / outcome_count) * 100.0),
        "failure_rate_pct": _round_pct((failure_count / outcome_count) * 100.0),
        "stall_rate_pct": _round_pct((stall_count / outcome_count) * 100.0),
    }


def _classify_edge(
    follow_through_rate_pct: float,
    failure_rate_pct: float,
    stall_rate_pct: float,
    outcome_count: int,
) -> Dict[str, str]:
    """
    Deterministic and conservative classification.

    Rules:
    - Low sample size stays cautious.
    - Strong constructive edge requires high follow-through and clear spread.
    - Strong fragile edge requires high failure and clear spread.
    - Strong indecisive edge requires high stall and clear spread.
    - Otherwise: mixed / no clear edge.
    """
    rates = [
        ("follow_through", follow_through_rate_pct),
        ("failure", failure_rate_pct),
        ("stall", stall_rate_pct),
    ]
    rates_sorted = sorted(rates, key=lambda item: item[1], reverse=True)
    top_label, top_rate = rates_sorted[0]
    _, second_rate = rates_sorted[1]
    spread = _round_pct(top_rate - second_rate)

    if outcome_count < 5:
        return {
            "edge_class": "low_sample",
            "operator_meaning": "There are too few labeled outcomes to treat this as a reliable edge.",
            "why_user_should_care": "Use the current signal cautiously. The history is too thin to support conviction.",
            "confidence_note": "Low sample size limits historical confidence.",
        }

    if top_label == "follow_through" and top_rate >= 60.0 and spread >= 15.0:
        return {
            "edge_class": "constructive",
            "operator_meaning": "Similar cases usually continue in the same direction.",
            "why_user_should_care": "This setup has a constructive historical bias, so confirmation carries more weight than usual.",
            "confidence_note": "Historical outcomes show a meaningful continuation bias.",
        }

    if top_label == "failure" and top_rate >= 60.0 and spread >= 15.0:
        return {
            "edge_class": "fragile",
            "operator_meaning": "Similar cases often reverse after the initial signal.",
            "why_user_should_care": "This setup has a weak historical track record, so initial strength should not be trusted on its own.",
            "confidence_note": "Historical outcomes show a meaningful reversal bias.",
        }

    if top_label == "stall" and top_rate >= 60.0 and spread >= 15.0:
        return {
            "edge_class": "indecisive",
            "operator_meaning": "Similar cases often stall rather than trend.",
            "why_user_should_care": "This setup may not offer enough directional follow-through to justify confidence without stronger confirmation.",
            "confidence_note": "Historical outcomes show a meaningful stall bias.",
        }

    return {
        "edge_class": "mixed",
        "operator_meaning": "Similar cases do not show a clear statistical edge.",
        "why_user_should_care": "The current signal should not be trusted on its own. Wait for stronger confirmation.",
        "confidence_note": "Historical outcomes are mixed rather than directional.",
    }


def _build_operator_summary(
    *,
    interpretation: OutcomeInterpretation,
    context_label: str,
) -> str:
    return (
        f"When similar {context_label} cases were labeled in history, "
        f"{interpretation.follow_through_rate_pct:.2f}% followed through, "
        f"{interpretation.failure_rate_pct:.2f}% failed, and "
        f"{interpretation.stall_rate_pct:.2f}% stalled. "
        f"{interpretation.operator_meaning}"
    )


def _normalize_counts_and_rates(
    *,
    outcome_count: int,
    outcome_counts: Dict[str, Any],
    follow_through_rate_pct: float,
    failure_rate_pct: float,
    stall_rate_pct: float,
) -> Dict[str, Any]:
    follow_through_count = _safe_int(outcome_counts.get("follow_through"))
    failure_count = _safe_int(outcome_counts.get("failure"))
    stall_count = _safe_int(outcome_counts.get("stall"))

    if (
        follow_through_rate_pct < 0.0
        or failure_rate_pct < 0.0
        or stall_rate_pct < 0.0
    ):
        derived = _derive_rates_from_counts(
            follow_through_count=follow_through_count,
            failure_count=failure_count,
            stall_count=stall_count,
            outcome_count=outcome_count,
        )
        follow_through_rate_pct = derived["follow_through_rate_pct"]
        failure_rate_pct = derived["failure_rate_pct"]
        stall_rate_pct = derived["stall_rate_pct"]

    return {
        "follow_through_count": follow_through_count,
        "failure_count": failure_count,
        "stall_count": stall_count,
        "follow_through_rate_pct": follow_through_rate_pct,
        "failure_rate_pct": failure_rate_pct,
        "stall_rate_pct": stall_rate_pct,
    }


def interpret_event_history_panel(event_history_panel: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convert historical event-linked outcomes into a deterministic operator-facing panel.
    """
    if not isinstance(event_history_panel, dict) or not event_history_panel:
        return None

    outcome_counts = event_history_panel.get("outcome_counts") or {}
    event_count = _safe_int(event_history_panel.get("event_count"))
    outcome_count = _safe_int(event_history_panel.get("outcome_count"))

    normalized = _normalize_counts_and_rates(
        outcome_count=outcome_count,
        outcome_counts=outcome_counts,
        follow_through_rate_pct=_safe_float(event_history_panel.get("follow_through_rate_pct"), default=-1.0),
        failure_rate_pct=_safe_float(event_history_panel.get("failure_rate_pct"), default=-1.0),
        stall_rate_pct=_safe_float(event_history_panel.get("stall_rate_pct"), default=-1.0),
    )

    edge = _classify_edge(
        follow_through_rate_pct=normalized["follow_through_rate_pct"],
        failure_rate_pct=normalized["failure_rate_pct"],
        stall_rate_pct=normalized["stall_rate_pct"],
        outcome_count=outcome_count,
    )

    historical_posture = event_history_panel.get("historical_posture") or "historically unclear"

    interpretation = OutcomeInterpretation(
        event_count=event_count,
        outcome_count=outcome_count,
        follow_through_count=normalized["follow_through_count"],
        failure_count=normalized["failure_count"],
        stall_count=normalized["stall_count"],
        follow_through_rate_pct=normalized["follow_through_rate_pct"],
        failure_rate_pct=normalized["failure_rate_pct"],
        stall_rate_pct=normalized["stall_rate_pct"],
        edge_class=edge["edge_class"],
        operator_meaning=edge["operator_meaning"],
        why_user_should_care=edge["why_user_should_care"],
        confidence_note=edge["confidence_note"],
    )

    operator_summary = _build_operator_summary(
        interpretation=interpretation,
        context_label="event-linked",
    )

    return {
        "panel_type": "labeled_outcomes",
        "status": "ok",
        "context_type": "event_history",
        "event_count": interpretation.event_count,
        "outcome_count": interpretation.outcome_count,
        "outcome_counts": {
            "follow_through": interpretation.follow_through_count,
            "failure": interpretation.failure_count,
            "stall": interpretation.stall_count,
        },
        "rates": {
            "follow_through_pct": interpretation.follow_through_rate_pct,
            "failure_pct": interpretation.failure_rate_pct,
            "stall_pct": interpretation.stall_rate_pct,
        },
        "edge_class": interpretation.edge_class,
        "historical_posture": historical_posture,
        "operator_meaning": interpretation.operator_meaning,
        "why_user_should_care": interpretation.why_user_should_care,
        "confidence_note": interpretation.confidence_note,
        "operator_summary": operator_summary,
    }


def interpret_setup_history_panel(setup_history_panel: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convert setup-history outcomes into the same deterministic labeled outcomes panel
    shape used by the operator explainer.

    Expected input shape (example):
    {
      "panel_type": "setup_history",
      "setup_type": "continuation",
      "pattern_count": 10,
      "outcome_count": 10,
      "follow_through_rate_pct": 0.0,
      "failure_rate_pct": 80.0,
      "stall_count": 2,
      "historical_posture": "historically fragile",
      ...
    }
    """
    if not isinstance(setup_history_panel, dict) or not setup_history_panel:
        return None

    outcome_count = _safe_int(setup_history_panel.get("outcome_count"))
    pattern_count = _safe_int(setup_history_panel.get("pattern_count"))
    setup_type = _safe_str(setup_history_panel.get("setup_type"), "setup")

    follow_through_rate_pct = _safe_float(setup_history_panel.get("follow_through_rate_pct"), default=-1.0)
    failure_rate_pct = _safe_float(setup_history_panel.get("failure_rate_pct"), default=-1.0)

    stall_count = _safe_int(setup_history_panel.get("stall_count"))
    stall_rate_pct = _safe_float(setup_history_panel.get("stall_rate_pct"), default=-1.0)

    # Setup-history panels often omit raw counts, so derive them from rates when needed.
    follow_through_count = _safe_int(setup_history_panel.get("follow_through_count"), default=-1)
    failure_count = _safe_int(setup_history_panel.get("failure_count"), default=-1)

    if outcome_count > 0:
        if follow_through_count < 0 and follow_through_rate_pct >= 0.0:
            follow_through_count = int(round((follow_through_rate_pct / 100.0) * outcome_count))
        if failure_count < 0 and failure_rate_pct >= 0.0:
            failure_count = int(round((failure_rate_pct / 100.0) * outcome_count))
        if stall_count <= 0 and follow_through_count >= 0 and failure_count >= 0:
            derived_stall = outcome_count - follow_through_count - failure_count
            stall_count = max(0, derived_stall)

    outcome_counts = {
        "follow_through": max(0, follow_through_count),
        "failure": max(0, failure_count),
        "stall": max(0, stall_count),
    }

    normalized = _normalize_counts_and_rates(
        outcome_count=outcome_count,
        outcome_counts=outcome_counts,
        follow_through_rate_pct=follow_through_rate_pct,
        failure_rate_pct=failure_rate_pct,
        stall_rate_pct=stall_rate_pct,
    )

    edge = _classify_edge(
        follow_through_rate_pct=normalized["follow_through_rate_pct"],
        failure_rate_pct=normalized["failure_rate_pct"],
        stall_rate_pct=normalized["stall_rate_pct"],
        outcome_count=outcome_count,
    )

    historical_posture = setup_history_panel.get("historical_posture") or "historically unclear"

    interpretation = OutcomeInterpretation(
        event_count=pattern_count,
        outcome_count=outcome_count,
        follow_through_count=normalized["follow_through_count"],
        failure_count=normalized["failure_count"],
        stall_count=normalized["stall_count"],
        follow_through_rate_pct=normalized["follow_through_rate_pct"],
        failure_rate_pct=normalized["failure_rate_pct"],
        stall_rate_pct=normalized["stall_rate_pct"],
        edge_class=edge["edge_class"],
        operator_meaning=edge["operator_meaning"],
        why_user_should_care=edge["why_user_should_care"],
        confidence_note=edge["confidence_note"],
    )

    operator_summary = _build_operator_summary(
        interpretation=interpretation,
        context_label=f"{setup_type}",
    )

    return {
        "panel_type": "labeled_outcomes",
        "status": "ok",
        "context_type": "setup_history",
        "setup_type": setup_type,
        "event_count": interpretation.event_count,
        "outcome_count": interpretation.outcome_count,
        "outcome_counts": {
            "follow_through": interpretation.follow_through_count,
            "failure": interpretation.failure_count,
            "stall": interpretation.stall_count,
        },
        "rates": {
            "follow_through_pct": interpretation.follow_through_rate_pct,
            "failure_pct": interpretation.failure_rate_pct,
            "stall_pct": interpretation.stall_rate_pct,
        },
        "edge_class": interpretation.edge_class,
        "historical_posture": historical_posture,
        "operator_meaning": interpretation.operator_meaning,
        "why_user_should_care": interpretation.why_user_should_care,
        "confidence_note": interpretation.confidence_note,
        "operator_summary": operator_summary,
    }


def build_labeled_outcomes_panel_from_source_2_summary(source_2_summary: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(source_2_summary, dict) or not source_2_summary:
        return None

    historical_context = source_2_summary.get("historical_context") or {}

    event_history_panel = historical_context.get("event_history_panel")
    setup_history_panel = historical_context.get("setup_history_panel")

    if isinstance(event_history_panel, dict) and event_history_panel:
        interpreted = interpret_event_history_panel(event_history_panel)
        if interpreted:
            return interpreted

    if isinstance(setup_history_panel, dict) and setup_history_panel:
        interpreted = interpret_setup_history_panel(setup_history_panel)
        if interpreted:
            return interpreted

    return None
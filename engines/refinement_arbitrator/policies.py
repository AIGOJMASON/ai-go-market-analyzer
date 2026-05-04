from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Optional, Tuple

AllowedDecision = Literal[
    "discard",
    "hold",
    "condition_for_child_core",
    "send_to_curved_mirror",
    "send_to_rosetta",
    "pass_to_pm",
]

ALLOWED_DECISIONS: Tuple[AllowedDecision, ...] = (
    "discard",
    "hold",
    "condition_for_child_core",
    "send_to_curved_mirror",
    "send_to_rosetta",
    "pass_to_pm",
)

DEFAULT_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    "discard": (0.00, 0.29),
    "hold": (0.30, 0.49),
    "condition_for_child_core": (0.50, 0.64),
    "send_to_engine_or_pass_to_pm_based_on_gap": (0.65, 0.79),
    "pass_to_pm": (0.80, 1.00),
}


@dataclass(frozen=True)
class EntropyState:
    entropy_status: Literal["low", "medium", "high"] = "medium"
    gravity_status: Literal["low", "medium", "high"] = "medium"
    grace_status: Literal["low", "medium", "high"] = "medium"


@dataclass(frozen=True)
class GapState:
    reasoning_missing: bool = False
    human_tempering_missing: bool = False
    severe_contamination_risk: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    recommended_action: AllowedDecision
    threshold_band: str
    justification_suffix: str


class PolicyError(ValueError):
    pass


def validate_decision(decision: str) -> AllowedDecision:
    if decision not in ALLOWED_DECISIONS:
        raise PolicyError(f"Illegal decision label: {decision}")
    return decision  # type: ignore[return-value]


def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 4)))


def apply_contamination_penalty(raw_fit: float, penalty: float) -> float:
    if penalty < 0:
        raise PolicyError("Contamination penalty cannot be negative.")
    return clamp_score(raw_fit - penalty)


def entropy_adjusted_thresholds(state: EntropyState) -> Dict[str, Tuple[float, float]]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    if state.entropy_status == "high" and state.gravity_status == "high" and state.grace_status == "low":
        thresholds["discard"] = (0.00, 0.34)
        thresholds["hold"] = (0.35, 0.54)
        thresholds["condition_for_child_core"] = (0.55, 0.69)
        thresholds["send_to_engine_or_pass_to_pm_based_on_gap"] = (0.70, 0.84)
        thresholds["pass_to_pm"] = (0.85, 1.00)
    elif state.entropy_status == "high":
        thresholds["discard"] = (0.00, 0.31)
        thresholds["hold"] = (0.32, 0.51)
        thresholds["condition_for_child_core"] = (0.52, 0.66)
        thresholds["send_to_engine_or_pass_to_pm_based_on_gap"] = (0.67, 0.81)
        thresholds["pass_to_pm"] = (0.82, 1.00)
    return thresholds


def band_for_score(score: float, state: Optional[EntropyState] = None) -> str:
    score = clamp_score(score)
    thresholds = entropy_adjusted_thresholds(state or EntropyState())
    for band, (low, high) in thresholds.items():
        if low <= score <= high:
            return band
    return "discard"


def decision_from_score(
    score: float,
    gap_state: Optional[GapState] = None,
    entropy_state: Optional[EntropyState] = None,
) -> PolicyDecision:
    score = clamp_score(score)
    gap_state = gap_state or GapState()
    entropy_state = entropy_state or EntropyState()
    band = band_for_score(score, entropy_state)

    if gap_state.severe_contamination_risk:
        if score >= 0.50:
            return PolicyDecision(
                recommended_action="condition_for_child_core",
                threshold_band=band,
                justification_suffix="Severe contamination risk blocked pass-through and forced core-specific conditioning.",
            )
        return PolicyDecision(
            recommended_action="hold",
            threshold_band=band,
            justification_suffix="Severe contamination risk prevented normal propagation.",
        )

    if gap_state.reasoning_missing and score >= 0.65:
        return PolicyDecision(
            recommended_action="send_to_curved_mirror",
            threshold_band=band,
            justification_suffix="Reasoning signal was insufficiently validated, so structural refinement was required first.",
        )

    if gap_state.human_tempering_missing and score >= 0.65:
        return PolicyDecision(
            recommended_action="send_to_rosetta",
            threshold_band=band,
            justification_suffix="Human-facing tempering was insufficient, so narrative refinement was required first.",
        )

    if band == "discard":
        return PolicyDecision("discard", band, "Composite score did not justify downstream cost.")
    if band == "hold":
        return PolicyDecision("hold", band, "Packet retained some value but was not yet fit for propagation.")
    if band == "condition_for_child_core":
        return PolicyDecision("condition_for_child_core", band, "Packet showed domain value but required child-core-aware conditioning.")
    if band == "send_to_engine_or_pass_to_pm_based_on_gap":
        return PolicyDecision("condition_for_child_core", band, "Packet was near PM-ready but still benefited from bounded conditioning before exposure.")
    return PolicyDecision("pass_to_pm", band, "Packet earned downstream PM review under current thresholds.")


def ensure_visible_scores(scores: Iterable[Tuple[str, Optional[float]]]) -> None:
    missing = [name for name, value in scores if value is None]
    if missing:
        joined = ", ".join(missing)
        raise PolicyError(f"Missing required visible scores: {joined}")
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from adapters import invoke_refinement_engines
from persistence import persist_arbitration_decision, persist_arbitration_receipt
from policies import (
    EntropyState,
    GapState,
    apply_contamination_penalty,
    clamp_score,
    decision_from_score,
    ensure_visible_scores,
)
from profiles import ChildCoreProfile, ProfileStore, contamination_penalty, infer_fit_score
from receipt import build_arbitration_id, build_receipt, utc_now


class ArbitrationError(ValueError):
    pass


REQUIRED_PACKET_FIELDS = [
    "packet_id",
    "source_core",
    "packet_type",
    "title",
    "summary",
    "source_refs",
    "trust_class",
    "confidence",
    "scope",
    "tags",
    "screening_status",
    "issuing_authority",
    "timestamp",
]


@dataclass(frozen=True)
class EngineSignals:
    reasoning_weight: float
    human_tempering_weight: float
    engine_invocations: List[Dict[str, Any]]


def validate_packet(packet: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_PACKET_FIELDS if field not in packet]
    if missing:
        raise ArbitrationError(f"Missing required packet fields: {', '.join(missing)}")
    if str(packet["source_core"]).lower() != "research_core":
        raise ArbitrationError("REFINEMENT_ARBITRATOR accepts only RESEARCH_CORE packets.")
    if str(packet["screening_status"]).lower() != "screened":
        raise ArbitrationError("Input packet must already be screened.")


def packet_text(packet: Mapping[str, Any]) -> str:
    parts = [
        str(packet.get("packet_type", "")),
        str(packet.get("title", "")),
        str(packet.get("summary", "")),
        " ".join(str(x) for x in packet.get("tags", [])),
        str(packet.get("target_core_hint") or ""),
        str(packet.get("domain_hint") or ""),
        str(packet.get("notes") or ""),
    ]
    return " | ".join(part for part in parts if part)


def compute_core_fit_scores(packet: Mapping[str, Any], store: ProfileStore) -> Dict[str, float]:
    text = packet_text(packet)
    results: Dict[str, float] = {}
    for profile in store.active():
        raw = infer_fit_score(text, profile)
        penalty = contamination_penalty(text, profile)
        results[profile.child_core_name] = apply_contamination_penalty(raw, penalty)
    return results


def pick_target_core(fit_scores: Dict[str, float]) -> Optional[str]:
    if not fit_scores:
        return None
    return max(fit_scores, key=fit_scores.get)


def compute_composite_weight(
    *,
    reasoning_weight: float,
    human_tempering_weight: float,
    fit_score: float,
    profile: ChildCoreProfile,
) -> float:
    composite = (
        reasoning_weight * profile.reasoning_coefficient
        + human_tempering_weight * profile.human_tempering_coefficient
        + fit_score * profile.core_fit_coefficient
    )
    return clamp_score(composite)


def build_gap_state(
    reasoning_weight: float,
    human_tempering_weight: float,
    packet: Mapping[str, Any],
    profile: ChildCoreProfile,
) -> GapState:
    text = packet_text(packet).lower()
    severe_contamination = contamination_penalty(text, profile) >= min(0.20, profile.max_contamination_penalty)
    return GapState(
        reasoning_missing=reasoning_weight < 0.55,
        human_tempering_missing=human_tempering_weight < 0.55,
        severe_contamination_risk=severe_contamination,
    )


def invoke_engines(packet: Mapping[str, Any], profile: ChildCoreProfile) -> EngineSignals:
    adapter_results = invoke_refinement_engines(packet, profile)
    invocations = [
        {
            "engine": adapter_results["curved_mirror"].engine,
            "status": adapter_results["curved_mirror"].status,
            "mode": adapter_results["curved_mirror"].mode,
            "notes": adapter_results["curved_mirror"].notes,
            "receipt_ref": None,
        },
        {
            "engine": adapter_results["rosetta"].engine,
            "status": adapter_results["rosetta"].status,
            "mode": adapter_results["rosetta"].mode,
            "notes": adapter_results["rosetta"].notes,
            "receipt_ref": None,
        },
    ]
    return EngineSignals(
        reasoning_weight=adapter_results["curved_mirror"].score,
        human_tempering_weight=adapter_results["rosetta"].score,
        engine_invocations=invocations,
    )


def run_arbitration(
    packet: Mapping[str, Any],
    *,
    entropy_state: Optional[EntropyState] = None,
    profile_store: Optional[ProfileStore] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    validate_packet(packet)
    entropy_state = entropy_state or EntropyState()
    profile_store = profile_store or ProfileStore()

    fit_scores = compute_core_fit_scores(packet, profile_store)
    target_core = pick_target_core(fit_scores)
    if target_core is None:
        raise ArbitrationError("No active child-core profiles were available.")

    profile = profile_store.get(target_core)
    signals = invoke_engines(packet, profile)
    fit_score = fit_scores[target_core]
    composite_weight = compute_composite_weight(
        reasoning_weight=signals.reasoning_weight,
        human_tempering_weight=signals.human_tempering_weight,
        fit_score=fit_score,
        profile=profile,
    )

    ensure_visible_scores([
        ("reasoning_weight", signals.reasoning_weight),
        ("human_tempering_weight", signals.human_tempering_weight),
        ("fit_score", fit_score),
        ("composite_weight", composite_weight),
    ])

    gap_state = build_gap_state(signals.reasoning_weight, signals.human_tempering_weight, packet, profile)
    policy_decision = decision_from_score(composite_weight, gap_state=gap_state, entropy_state=entropy_state)

    arbitration_id = build_arbitration_id()
    justification = (
        f"Target core {target_core} received the highest fit score ({fit_score:.2f}). "
        f"Reasoning weight={signals.reasoning_weight:.2f}, human tempering weight={signals.human_tempering_weight:.2f}, "
        f"composite weight={composite_weight:.2f}. {policy_decision.justification_suffix}"
    )

    result: Dict[str, Any] = {
        "arbitration_id": arbitration_id,
        "source_packet_id": str(packet["packet_id"]),
        "issuing_layer": "REFINEMENT_ARBITRATOR",
        "reasoning_weight": signals.reasoning_weight,
        "human_tempering_weight": signals.human_tempering_weight,
        "child_core_fit_scores": fit_scores,
        "composite_weight": composite_weight,
        "recommended_action": policy_decision.recommended_action,
        "justification_summary": justification,
        "timestamp": utc_now(),
        "target_child_core": target_core,
        "engine_invocations": signals.engine_invocations,
        "entropy_status": entropy_state.entropy_status,
        "gravity_status": entropy_state.gravity_status,
        "grace_status": entropy_state.grace_status,
        "decision_threshold_band": policy_decision.threshold_band,
        "hold_reason": justification if policy_decision.recommended_action == "hold" else None,
        "discard_reason": justification if policy_decision.recommended_action == "discard" else None,
        "condition_profile_ref": profile.child_core_id,
        "coefficients_used": profile.coefficients(),
    }

    receipt = build_receipt(
        arbitration_id=arbitration_id,
        source_packet_id=str(packet["packet_id"]),
        recommended_action=policy_decision.recommended_action,
        reasoning_weight=signals.reasoning_weight,
        human_tempering_weight=signals.human_tempering_weight,
        child_core_fit_scores=fit_scores,
        composite_weight=composite_weight,
        engine_invocations=signals.engine_invocations,
        target_child_core=target_core,
        threshold_band=policy_decision.threshold_band,
        justification_summary=justification,
    )
    result["receipt"] = receipt
    result["receipt_ref"] = receipt["arbitration_id"]

    if persist:
        result["decision_path"] = persist_arbitration_decision(result)
        result["receipt_path"] = persist_arbitration_receipt(receipt)

    return result
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from AI_GO.engines.engine_confidence_conservation import (
    evaluate_engine_confidence_conservation,
)
from AI_GO.engines.engine_drift_guard import attach_drift_seal_to_handoff
from AI_GO.engines.engine_output_registry import validate_engine_output_registry
from AI_GO.engines.engine_signal_contract import (
    build_engine_interpretation_packet,
    validate_engine_interpretation_packet,
)


CURATED_CHILD_CORE_HANDOFF_ENGINE_VERSION = "v5C.4"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_0_1(value: Any) -> float:
    number = _safe_float(value, 0.0)
    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0
    return number


def _research_packet_id(research_packet: dict[str, Any]) -> str:
    return (
        _safe_str(research_packet.get("research_packet_id"))
        or _safe_str(research_packet.get("packet_id"))
        or _safe_str(research_packet.get("id"))
    )


def _interpretation_class(pre_weight: float, trust_class: str) -> str:
    if trust_class == "blocked" or pre_weight <= 0:
        return "blocked"
    if pre_weight < 0.55:
        return "weak_context"
    if pre_weight < 0.8:
        return "bounded_context"
    return "strong_curated_context"


def _derive_direction(*, price_change_pct: float, confirmation: str) -> str:
    if confirmation == "none":
        return "unknown"
    if price_change_pct > 0:
        return "positive"
    if price_change_pct < 0:
        return "negative"
    return "neutral"


def _derive_interpretation_type(targets: list[Any]) -> str:
    clean_targets = {_safe_str(target) for target in targets}
    if "market_analyzer_v1" in clean_targets:
        return "market_event_context"
    if "contractor_builder_v1" in clean_targets:
        return "contractor_external_pressure"
    return "unknown_context"


def _derive_classification(*, signal_type: str, sector: str, trust_class: str) -> str:
    if trust_class == "blocked":
        return "blocked"
    if signal_type:
        return signal_type
    if sector:
        return f"{sector}_context"
    return "unknown"


def _derive_summary(research_input: dict[str, Any], interpretation_class: str) -> str:
    title = _safe_str(research_input.get("title"))
    summary = _safe_str(research_input.get("summary"))
    symbol = _safe_str(research_input.get("symbol")).upper()

    base = summary or title or "Governed research packet interpreted by engine."

    if symbol:
        return f"{symbol}: {base} Interpretation class: {interpretation_class}."

    return f"{base} Interpretation class: {interpretation_class}."


def _build_curated_packet(
    *,
    research_packet: dict[str, Any],
    interpretation_class: str,
    target_child_core: str,
) -> dict[str, Any]:
    research_input = _safe_dict(research_packet.get("research_input"))
    trust = _safe_dict(research_packet.get("trust"))

    return {
        "signal_type": _safe_str(research_input.get("signal_type")),
        "title": _safe_str(research_input.get("title")),
        "summary": _safe_str(research_input.get("summary")),
        "symbol": _safe_str(research_input.get("symbol")).upper(),
        "symbols": _safe_list(research_input.get("symbols")),
        "price": research_input.get("price"),
        "price_change_pct": _safe_float(research_input.get("price_change_pct"), 0.0),
        "sector": _safe_str(research_input.get("sector")) or "unknown",
        "confirmation": _safe_str(research_input.get("confirmation")) or "partial",
        "observed_at": _safe_str(research_input.get("observed_at")),
        "source_refs": _safe_list(research_input.get("source_refs")),
        "pre_weight": _clamp_0_1(trust.get("pre_weight", 0.0)),
        "trust_class": _safe_str(trust.get("trust_class")),
        "interpretation_class": interpretation_class,
        "target_child_core": target_child_core,
        "engine_interpreted": True,
        "raw_provider_payload_allowed": False,
        "downstream_reweighting_allowed": False,
        "child_core_reinterpretation_allowed": False,
    }


def curate_research_packet_for_child_cores(
    research_packet: dict[str, Any],
) -> dict[str, Any]:
    research = _safe_dict(research_packet)
    trust = _safe_dict(research.get("trust"))
    research_input = _safe_dict(research.get("research_input"))
    routing = _safe_dict(research.get("routing"))
    screening = _safe_dict(research.get("screening"))

    pre_weight = _clamp_0_1(trust.get("pre_weight", 0.0))
    trust_class = _safe_str(trust.get("trust_class")) or "unknown"
    interpretation_class = _interpretation_class(pre_weight, trust_class)

    targets = _safe_list(routing.get("child_core_targets")) or _safe_list(
        research_input.get("child_core_targets")
    )
    target_child_core = _safe_str(targets[0]) if targets else ""

    symbol = _safe_str(research_input.get("symbol")).upper()
    price_change_pct = _safe_float(research_input.get("price_change_pct"), 0.0)
    sector = _safe_str(research_input.get("sector"))
    confirmation = _safe_str(research_input.get("confirmation")) or "unknown"
    signal_type = _safe_str(research_input.get("signal_type"))

    allowed = bool(screening.get("valid")) and interpretation_class not in {
        "blocked",
        "weak_context",
    }

    interpretation_packet = build_engine_interpretation_packet(
        engine_id="curated_child_core_handoff_engine",
        source_research_packet=research,
        interpretation_type=_derive_interpretation_type(targets),
        direction=_derive_direction(
            price_change_pct=price_change_pct,
            confirmation=confirmation,
        ),
        confidence=pre_weight,
        weight=pre_weight,
        classification=_derive_classification(
            signal_type=signal_type,
            sector=sector,
            trust_class=trust_class,
        ),
        summary=_derive_summary(research_input, interpretation_class),
        evidence_signals=[
            signal
            for signal in [
                f"trust_class:{trust_class}" if trust_class else "",
                f"pre_weight:{pre_weight}",
                f"screening_valid:{bool(screening.get('valid') is True)}",
                f"symbol:{symbol}" if symbol else "",
                f"sector:{sector}" if sector else "",
                f"confirmation:{confirmation}" if confirmation else "",
            ]
            if signal
        ],
        constraints=[
            "engine_interpretation_only",
            "no_execution_authority",
            "no_state_mutation_authority",
            "no_downstream_reweighting",
            "no_child_core_reinterpretation",
            "confidence_conservation_required",
            "weight_conservation_required",
        ],
    )

    signal_integrity = validate_engine_interpretation_packet(interpretation_packet)
    registry_decision = validate_engine_output_registry(interpretation_packet)
    conservation_decision = evaluate_engine_confidence_conservation(
        research_packet=research,
        engine_interpretation_packet=interpretation_packet,
    )

    if signal_integrity.get("allowed") is not True:
        allowed = False

    if registry_decision.get("allowed") is not True:
        allowed = False

    if conservation_decision.get("allowed") is not True:
        allowed = False

    research_packet_id = _research_packet_id(research)
    curated_packet = _build_curated_packet(
        research_packet=research,
        interpretation_class=interpretation_class,
        target_child_core=target_child_core,
    )

    handoff = {
        "artifact_type": "curated_child_core_handoff_packet",
        "artifact_version": CURATED_CHILD_CORE_HANDOFF_ENGINE_VERSION,
        "generated_at": _utc_now_iso(),
        "created_at": _utc_now_iso(),
        "sealed": True,
        "bounded": True,
        "source_authority": "engines",
        "root_spine_authority": "root_intelligence_spine",
        "engine_id": "curated_child_core_handoff_engine",
        "target_child_core": target_child_core,
        "spine_order": [
            "RESEARCH_CORE",
            "engines",
            "child_core_consumption_adapter",
            "child_core",
        ],
        "authority": {
            "authority_id": "engines",
            "curates_before_child_core": True,
            "multi_child_core_handoff": True,
            "can_execute": False,
            "can_mutate_child_core": False,
            "can_override_research": False,
            "can_override_governance": False,
            "can_write_external_memory": False,
            "execution_authority": False,
            "canon_authority": False,
            "governance_override": False,
            "watcher_override": False,
            "state_mutation_authority": False,
            "external_memory_write_authority": False,
            "raw_research_authority": False,
            "downstream_reweighting_authority": False,
            "child_core_reinterpretation_authority": False,
        },
        "source": {
            "research_packet_id": research_packet_id,
            "origin_authority": "RESEARCH_CORE",
            "research_artifact_type": research.get("artifact_type"),
            "source_valid": bool(screening.get("valid") is True),
            "screening_valid": bool(screening.get("valid") is True),
            "trust_class": trust_class,
            "pre_weight": pre_weight,
        },
        "lineage": {
            "research_packet_id": research_packet_id,
            "interpretation_packet_id": interpretation_packet.get("source_research_packet_id"),
            "engine_id": "curated_child_core_handoff_engine",
            "adapter_id": (
                "market_analyzer_root_handoff_input"
                if target_child_core == "market_analyzer_v1"
                else "contractor_builder_root_handoff_input"
            ),
        },
        "curation": {
            "status": "passed" if allowed else "held",
            "interpretation_class": interpretation_class,
            "drift_risk": (
                "low"
                if pre_weight >= 0.8
                else "medium"
                if pre_weight >= 0.55
                else "high"
            ),
            "hallucination_controls": {
                "raw_provider_payload_hidden_from_child_core": True,
                "unsupported_expansion_allowed": False,
                "must_preserve_source_refs": True,
                "must_preserve_pre_weight": True,
                "engine_interpretation_required": True,
                "engine_drift_guard_required": True,
                "engine_output_registry_required": True,
                "engine_confidence_conservation_required": True,
            },
        },
        "child_core_handoff": {
            "allowed": allowed,
            "targets": targets,
            "primary_child_core": target_child_core,
            "packet": curated_packet,
        },
        "research_packet_view": {
            "provider": _safe_str(research_input.get("provider")),
            "provider_kind": _safe_str(research_input.get("provider_kind")),
            "signal_type": signal_type,
            "symbol": symbol,
            "sector": sector,
            "confirmation": confirmation,
            "title": _safe_str(research_input.get("title")),
            "summary": _safe_str(research_input.get("summary")),
        },
        "curated_packet": curated_packet,
        "engine_interpretation_packet": interpretation_packet,
        "engine_signal_integrity": signal_integrity,
        "engine_output_registry": registry_decision,
        "engine_confidence_conservation": conservation_decision,
        "interpretation_class": interpretation_class,
        "allowed_for_child_core": allowed,
        "external_source": True,
        "raw_input": False,
    }

    return attach_drift_seal_to_handoff(handoff)
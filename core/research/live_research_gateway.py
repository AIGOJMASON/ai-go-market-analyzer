from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


LIVE_RESEARCH_GATEWAY_VERSION = "v1.1"

SOURCE_QUALITY_WEIGHTS = {
    "official": 1.0,
    "verified_api": 0.9,
    "operator_manual": 0.75,
    "vendor": 0.7,
    "newswire": 0.65,
    "rss_feed": 0.55,
    "social_observation": 0.35,
    "unknown": 0.25,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _source_weight(source_type: str) -> float:
    return SOURCE_QUALITY_WEIGHTS.get(source_type, SOURCE_QUALITY_WEIGHTS["unknown"])


def _trust_class(pre_weight: float) -> str:
    if pre_weight >= 0.8:
        return "high_trust"
    if pre_weight >= 0.55:
        return "bounded_trust"
    if pre_weight > 0:
        return "low_trust"
    return "blocked"


def _derive_pre_weight(
    *,
    source_type: str,
    source_material: list[Any],
    source_refs: list[Any],
    provider_payload: dict[str, Any],
) -> float:
    base = _source_weight(source_type)
    material_bonus = min(0.10, 0.025 * len(source_material))
    ref_bonus = min(0.10, 0.05 * len(source_refs))
    provider_bonus = 0.05 if provider_payload else 0.0
    return round(min(1.0, base + material_bonus + ref_bonus + provider_bonus), 3)


def build_live_research_packet(payload: dict[str, Any]) -> dict[str, Any]:
    source = _safe_dict(payload)

    source_type = _safe_str(source.get("source_type")) or "unknown"
    signal_type = _safe_str(source.get("signal_type")) or "live_information"
    child_core_targets = _safe_list(source.get("child_core_targets"))
    child_core_id = _safe_str(source.get("child_core_id"))

    if child_core_id and child_core_id not in child_core_targets:
        child_core_targets.append(child_core_id)

    source_material = _safe_list(source.get("source_material"))
    source_refs = _safe_list(source.get("source_refs") or source.get("references"))
    provider_payload = _safe_dict(source.get("provider_payload"))

    title = _safe_str(source.get("title") or source.get("headline"))
    summary = _safe_str(source.get("summary") or source.get("description"))

    errors: list[str] = []
    warnings: list[str] = []

    if not title:
        errors.append("missing_title")
    if not summary:
        warnings.append("missing_summary")
    if not child_core_targets:
        warnings.append("no_child_core_targets_declared")

    pre_weight = 0.0 if errors else _derive_pre_weight(
        source_type=source_type,
        source_material=source_material,
        source_refs=source_refs,
        provider_payload=provider_payload,
    )

    packet_id = (
        "research_live_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
        f"{uuid4().hex[:10]}"
    )

    return {
        "artifact_type": "live_research_packet",
        "artifact_version": LIVE_RESEARCH_GATEWAY_VERSION,
        "packet_id": packet_id,
        "generated_at": _utc_now_iso(),
        "sealed": True,
        "authority": {
            "authority_id": "RESEARCH_CORE",
            "root_intake_gate": True,
            "pre_weighting": True,
            "multi_child_core_source": True,
            "can_execute": False,
            "can_mutate_child_core": False,
            "can_interpret_strategy": False,
            "can_write_external_memory": False,
            "can_override_engines": False,
            "can_override_pm": False,
            "can_override_governance": False,
        },
        "screening": {
            "status": "blocked" if errors else "passed",
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
        },
        "research_input": {
            "signal_type": signal_type,
            "source_type": source_type,
            "provider": _safe_str(source.get("provider")),
            "provider_kind": _safe_str(source.get("provider_kind")),
            "title": title,
            "summary": summary,
            "symbol": _safe_str(source.get("symbol")).upper(),
            "symbols": _safe_list(source.get("symbols")),
            "price": source.get("price"),
            "price_change_pct": source.get("price_change_pct"),
            "sector": _safe_str(source.get("sector") or "unknown"),
            "confirmation": _safe_str(source.get("confirmation") or "partial"),
            "observed_at": _safe_str(source.get("observed_at")),
            "provider_payload": provider_payload,
            "source_material": source_material,
            "source_refs": source_refs,
            "intake_context": _safe_dict(source.get("intake_context") or source.get("context")),
        },
        "routing": {
            "child_core_targets": child_core_targets,
            "primary_child_core": child_core_targets[0] if child_core_targets else "",
            "must_pass_engines_before_child_core": True,
        },
        "trust": {
            "source_quality_weight": _source_weight(source_type),
            "pre_weight": pre_weight,
            "trust_class": _trust_class(pre_weight),
        },
        "handoff": {
            "next_authority": "engines",
            "downstream_allowed": not errors,
        },
    }
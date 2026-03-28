from __future__ import annotations

import importlib
from typing import Any, Callable, Dict, Optional, Tuple

try:
    from AI_GO.EXTERNAL_MEMORY.qualification.qualification_engine import (
        qualify_external_memory_candidate,
    )
    from AI_GO.EXTERNAL_MEMORY.persistence.persistence_gate import (
        apply_persistence_gate,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.qualification.qualification_engine import (
        qualify_external_memory_candidate,
    )
    from EXTERNAL_MEMORY.persistence.persistence_gate import (
        apply_persistence_gate,
    )


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _source_quality_weight(payload: Dict[str, Any]) -> float:
    source_quality = payload.get("source_quality")
    if source_quality is not None:
        return _safe_float(source_quality, 0.0)

    confirmation = str(payload.get("confirmation", "")).strip().lower()
    source_type = str(payload.get("source_type", "live_market_input")).strip().lower()

    score = 30.0
    if confirmation == "confirmed":
        score += 10.0
    elif confirmation == "partial":
        score += 2.0
    elif confirmation == "unconfirmed":
        score -= 8.0

    if source_type in {"official_filing", "exchange_feed", "first_party_operator"}:
        score += 10.0
    elif source_type in {"rumor_feed", "social_scrape", "anonymous_tip"}:
        score -= 10.0

    return max(0.0, min(score, 50.0))


def _signal_quality_weight(payload: Dict[str, Any]) -> float:
    score = 10.0

    headline = payload.get("headline")
    if isinstance(headline, str) and headline.strip():
        score += 6.0

    symbol = payload.get("symbol")
    if isinstance(symbol, str) and symbol.strip():
        score += 4.0

    sector = payload.get("sector")
    if isinstance(sector, str) and sector.strip():
        score += 3.0

    price_change_pct = payload.get("price_change_pct")
    if isinstance(price_change_pct, (int, float)):
        score += min(abs(float(price_change_pct)), 7.0)

    return max(0.0, min(score, 25.0))


def _domain_relevance_weight(payload: Dict[str, Any]) -> float:
    core_id = str(payload.get("target_core_id", "market_analyzer_v1")).strip().lower()
    symbol = payload.get("symbol")
    sector = payload.get("sector")

    score = 8.0
    if core_id == "market_analyzer_v1":
        score += 8.0
    if isinstance(symbol, str) and symbol.strip():
        score += 5.0
    if isinstance(sector, str) and sector.strip():
        score += 4.0

    return max(0.0, min(score, 20.0))


def _persistence_value_weight(payload: Dict[str, Any]) -> float:
    score = 5.0

    confirmation = str(payload.get("confirmation", "")).strip().lower()
    if confirmation == "confirmed":
        score += 6.0
    elif confirmation == "partial":
        score += 2.0

    price_change_pct = payload.get("price_change_pct")
    if isinstance(price_change_pct, (int, float)):
        magnitude = abs(float(price_change_pct))
        if magnitude >= 3.0:
            score += 6.0
        elif magnitude >= 1.0:
            score += 3.0

    headline = str(payload.get("headline", "")).strip().lower()
    if headline:
        if any(term in headline for term in ["confirmed", "official", "filing", "earnings", "guidance"]):
            score += 4.0

    return max(0.0, min(score, 20.0))


def _contamination_penalty(payload: Dict[str, Any]) -> float:
    penalty = 0.0

    confirmation = str(payload.get("confirmation", "")).strip().lower()
    if confirmation == "unconfirmed":
        penalty += 10.0
    elif confirmation == "partial":
        penalty += 3.0

    source_type = str(payload.get("source_type", "")).strip().lower()
    if source_type in {"rumor_feed", "social_scrape", "anonymous_tip"}:
        penalty += 8.0

    return max(0.0, min(penalty, 20.0))


def _redundancy_penalty(payload: Dict[str, Any]) -> float:
    redundancy = payload.get("redundancy_penalty")
    if redundancy is not None:
        return max(0.0, min(_safe_float(redundancy, 0.0), 20.0))
    return 0.0


def _trust_class(payload: Dict[str, Any]) -> str:
    trust_class = str(payload.get("trust_class", "")).strip().lower()
    if trust_class:
        return trust_class

    confirmation = str(payload.get("confirmation", "")).strip().lower()
    if confirmation == "confirmed":
        return "verified"
    if confirmation == "partial":
        return "caution"
    return "unverifiable"


def _target_child_cores(payload: Dict[str, Any]) -> list[str]:
    targets = payload.get("target_child_cores")
    if isinstance(targets, list) and targets:
        return [str(item) for item in targets]
    return [str(payload.get("target_core_id", "market_analyzer_v1"))]


def build_external_memory_signal(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_type": "governed_external_signal",
        "source_type": str(payload.get("source_type", "live_market_input")),
        "source_quality_weight": _source_quality_weight(payload),
        "signal_quality_weight": _signal_quality_weight(payload),
        "domain_relevance_weight": _domain_relevance_weight(payload),
        "persistence_value_weight": _persistence_value_weight(payload),
        "contamination_penalty": _contamination_penalty(payload),
        "redundancy_penalty": _redundancy_penalty(payload),
        "trust_class": _trust_class(payload),
        "payload": {
            "request_id": payload.get("request_id"),
            "headline": payload.get("headline"),
            "symbol": payload.get("symbol"),
            "sector": payload.get("sector"),
            "price_change_pct": payload.get("price_change_pct"),
            "confirmation": payload.get("confirmation"),
            "event_theme": payload.get("event_theme"),
            "macro_bias": payload.get("macro_bias"),
        },
        "target_child_cores": _target_child_cores(payload),
        "provenance": {
            "source_ref": payload.get("source_ref", payload.get("request_id")),
            "request_id": payload.get("request_id"),
            "origin_surface": payload.get("origin_surface", "market_analyzer_live"),
            "route_mode": payload.get("route_mode"),
        },
    }


def build_external_memory_panel(
    qualification_record: Dict[str, Any],
    persistence_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "state": "present",
        "qualification_decision": qualification_record.get("decision"),
        "persistence_decision": persistence_receipt.get("persistence_decision"),
        "source_type": qualification_record.get("source_type"),
        "source_quality_weight": qualification_record.get("source_quality_weight"),
        "adjusted_weight": qualification_record.get("adjusted_weight"),
        "trust_class": qualification_record.get("trust_class"),
        "rejection_reason": persistence_receipt.get("rejection_reason")
        or qualification_record.get("rejection_reason"),
        "memory_id": persistence_receipt.get("memory_id"),
        "qualification_record_id": qualification_record.get("qualification_record_id"),
    }


def _resolve_callable(
    module_names: tuple[str, ...],
    candidate_function_names: tuple[str, ...],
) -> Optional[Callable[..., Dict[str, Any]]]:
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        for function_name in candidate_function_names:
            candidate = getattr(module, function_name, None)
            if callable(candidate):
                return candidate

    return None


def _invoke_callable(
    fn: Callable[..., Dict[str, Any]],
    *,
    payload: Dict[str, Any],
    artifact: Dict[str, Any] | None = None,
    receipt: Dict[str, Any] | None = None,
) -> Optional[Dict[str, Any]]:
    attempts = []

    if artifact is not None and receipt is not None:
        attempts.extend(
            [
                lambda: fn(artifact, receipt),
                lambda: fn(source_artifact=artifact, source_receipt=receipt),
                lambda: fn(retrieval_artifact=artifact, retrieval_receipt=receipt),
                lambda: fn(promotion_artifact=artifact, promotion_receipt=receipt),
            ]
        )

    attempts.extend(
        [
            lambda: fn(payload),
            lambda: fn(request=payload),
            lambda: fn(**payload),
        ]
    )

    for attempt in attempts:
        try:
            result = attempt()
        except TypeError:
            continue
        except Exception:
            return None

        if isinstance(result, dict):
            return result

    return None


def _extract_artifact_and_receipt(
    result: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    if not isinstance(result, dict):
        return None, None

    artifact = result.get("artifact")
    receipt = result.get("receipt")

    if isinstance(artifact, dict) and isinstance(receipt, dict):
        return artifact, receipt

    if result.get("artifact_type") and result.get("receipt_type"):
        return result, result

    for artifact_key, receipt_key in (
        ("retrieval_artifact", "retrieval_receipt"),
        ("promotion_artifact", "promotion_receipt"),
        ("source_artifact", "source_receipt"),
    ):
        candidate_artifact = result.get(artifact_key)
        candidate_receipt = result.get(receipt_key)
        if isinstance(candidate_artifact, dict) and isinstance(candidate_receipt, dict):
            return candidate_artifact, candidate_receipt

    return None, None


def _build_retrieval_payload(
    payload: Dict[str, Any],
    qualification_record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "requester_profile": "market_analyzer_reader",
        "symbol": payload.get("symbol"),
        "sector": payload.get("sector"),
        "trust_class": qualification_record.get("trust_class"),
        "source_type": payload.get("source_type", "live_market_input"),
        "limit": 10,
        "min_adjusted_weight": None,
    }


def _run_retrieval(
    payload: Dict[str, Any],
    qualification_record: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    try:
        from AI_GO.child_cores.market_analyzer_v1.external_memory.retrieval_path import (
            run_market_analyzer_external_memory_retrieval,
        )
    except ModuleNotFoundError:
        from child_cores.market_analyzer_v1.external_memory.retrieval_path import (
            run_market_analyzer_external_memory_retrieval,
        )

    retrieval_payload = _build_retrieval_payload(payload, qualification_record)

    try:
        retrieval_result = run_market_analyzer_external_memory_retrieval(
            **retrieval_payload
        )
    except Exception as exc:
        return {
            "artifact_type": "external_memory_retrieval_error",
            "error": str(exc),
            "payload_used": retrieval_payload,
        }, None, None

    if not isinstance(retrieval_result, dict):
        return None, None, None

    artifact = (
        retrieval_result.get("artifact")
        or retrieval_result.get("retrieval_artifact")
    )
    receipt = (
        retrieval_result.get("receipt")
        or retrieval_result.get("retrieval_receipt")
    )

    return retrieval_result, artifact, receipt


def _build_promotion_payload(
    payload: Dict[str, Any],
    qualification_record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "requester_profile": "market_analyzer_reader",
        "symbol": payload.get("symbol"),
        "sector": payload.get("sector"),
        "trust_class": qualification_record.get("trust_class"),
        "source_type": payload.get("source_type", "live_market_input"),
        "limit": 10,
        "min_adjusted_weight": None,
    }


def _run_promotion(
    payload: Dict[str, Any],
    qualification_record: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    try:
        from AI_GO.child_cores.market_analyzer_v1.external_memory.promotion_path import (
            run_market_analyzer_external_memory_promotion,
        )
    except ModuleNotFoundError:
        from child_cores.market_analyzer_v1.external_memory.promotion_path import (
            run_market_analyzer_external_memory_promotion,
        )

    promotion_payload = _build_promotion_payload(payload, qualification_record)

    try:
        promotion_result = run_market_analyzer_external_memory_promotion(
            **promotion_payload
        )
    except Exception as exc:
        return {
            "artifact_type": "external_memory_promotion_error",
            "error": str(exc),
            "payload_used": promotion_payload,
        }, None, None

    if not isinstance(promotion_result, dict):
        return None, None, None

    artifact = (
        promotion_result.get("artifact")
        or promotion_result.get("promotion_artifact")
    )
    receipt = (
        promotion_result.get("receipt")
        or promotion_result.get("promotion_receipt")
    )

    return promotion_result, artifact, receipt


def run_external_memory_runtime_path(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    signal = build_external_memory_signal(payload)
    qualification = qualify_external_memory_candidate(signal)
    persistence_receipt = apply_persistence_gate(qualification.record)

    result: Dict[str, Any] = {
        "artifact_type": "external_memory_runtime_result",
        "status": "ok",
        "qualification_decision": qualification.record.get("decision"),
        "qualification_record": qualification.record,
        "qualification_receipt": qualification.receipt,
        "persistence_receipt": persistence_receipt,
        "panel": build_external_memory_panel(
            qualification_record=qualification.record,
            persistence_receipt=persistence_receipt,
        ),
    }

    if qualification.record.get("decision") != "persist_candidate":
        return result

    if persistence_receipt.get("persistence_decision") != "committed":
        return result

    retrieval_result, retrieval_artifact, retrieval_receipt = _run_retrieval(
        payload=payload,
        qualification_record=qualification.record,
    )
    if retrieval_result is not None:
        result["external_memory_retrieval_result"] = retrieval_result
    if retrieval_artifact is not None:
        result["external_memory_retrieval_artifact"] = retrieval_artifact
    if retrieval_receipt is not None:
        result["external_memory_retrieval_receipt"] = retrieval_receipt

    promotion_result, promotion_artifact, promotion_receipt = _run_promotion(
        payload=payload,
        qualification_record=qualification.record,
    )
    if promotion_result is not None:
        result["external_memory_promotion_result"] = promotion_result
    if promotion_artifact is not None:
        result["external_memory_promotion_artifact"] = promotion_artifact
    if promotion_receipt is not None:
        result["external_memory_promotion_receipt"] = promotion_receipt

    return result

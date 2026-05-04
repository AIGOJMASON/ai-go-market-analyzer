from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Set


WATCHER_VERSION = "v5B.4.2"


HIGH_CODES = {
    "forbidden_authority_claim",
    "raw_external_child_core_bypass",
    "root_spine_order_invalid",
    "root_spine_required_links_missing",
    "execution_missing_execution_gate_available",
    "execution_missing_execution_gate_passed",
    "bypass_execution_gate",
}


MEDIUM_CODES = {
    "research_core_lineage_missing",
    "engine_lineage_missing",
    "adapter_lineage_missing",
    "watcher_required",
    "watcher_enforcement_missing",
}


LOW_CODES = {
    "legacy_raw_live_route_disabled",
    "raw_live_payload_rejected",
    "curated_engine_handoff_packet_missing",
    "curated_engine_handoff_shape_invalid",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


# 🔴 FIXED: NO RECURSION
def _extract_reason_codes(decision: Dict[str, Any]) -> List[str]:
    codes: Set[str] = set()

    # top-level reasons
    for r in _safe_list(decision.get("reasons")):
        if isinstance(r, dict):
            code = _safe_str(r.get("code"))
            if code:
                codes.add(code)

    # one-level nested only (no recursion)
    for key in ("execution_gate", "cross_core_enforcement", "route_enforcement"):
        nested = _safe_dict(decision.get(key))

        for r in _safe_list(nested.get("reasons")):
            if isinstance(r, dict):
                code = _safe_str(r.get("code"))
                if code:
                    codes.add(code)

    return sorted(codes)


def _classify_violation_from_codes(codes: Set[str]) -> str:
    if "forbidden_authority_claim" in codes:
        return "authority_inflation"

    if "raw_external_child_core_bypass" in codes:
        return "cross_core_bypass"

    if "root_spine_order_invalid" in codes or "root_spine_required_links_missing" in codes:
        return "invalid_spine_order"

    if "research_core_lineage_missing" in codes:
        return "missing_lineage"

    if "engine_lineage_missing" in codes:
        return "missing_engine_processing"

    if "adapter_lineage_missing" in codes:
        return "missing_adapter_layer"

    if "legacy_raw_live_route_disabled" in codes:
        return "route_violation"

    if "curated_engine_handoff_packet_missing" in codes:
        return "missing_curated_packet"

    if "curated_engine_handoff_shape_invalid" in codes:
        return "invalid_curated_packet"

    if "raw_live_payload_rejected" in codes:
        return "raw_payload_rejected"

    if any(code.startswith("execution_") for code in codes):
        return "execution_violation"

    return "unknown_violation"


def _severity_from_codes(codes: Set[str]) -> str:
    if codes & HIGH_CODES:
        return "high"

    if codes & MEDIUM_CODES:
        return "medium"

    if codes & LOW_CODES:
        return "low"

    return "unknown"


def _build_summary(decision: Dict[str, Any]) -> str:
    message = _safe_str(decision.get("message"))

    for r in _safe_list(decision.get("reasons")):
        if isinstance(r, dict):
            msg = _safe_str(r.get("message"))
            if msg:
                return msg

    return message or "Enforcement violation detected."


def record_enforcement_violation(
    *,
    layer: str,
    decision: Dict[str, Any],
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    ctx = _safe_dict(context)
    decision_safe = _safe_dict(decision)

    reason_codes = _extract_reason_codes(decision_safe)
    code_set = set(reason_codes)

    violation_type = _classify_violation_from_codes(code_set)
    severity = _severity_from_codes(code_set)

    return {
        "artifact_type": "enforcement_violation_record",
        "artifact_version": WATCHER_VERSION,
        "timestamp": _utc_now_iso(),
        "layer": _safe_str(layer),
        "violation_type": violation_type,
        "severity": severity,
        "reason_codes": reason_codes,
        "summary": _build_summary(decision_safe),
        "decision": decision_safe,
        "context": {
            "route": _safe_str(ctx.get("route")),
            "method": _safe_str(ctx.get("method")),
            "actor": _safe_str(ctx.get("actor")),
            "request_id": _safe_str(ctx.get("request_id")),
        },
        "policy": {
            "execution_allowed": False,
            "mutation_allowed": False,
            "watcher_is_observer_only": True,
            "max_severity_classification": True,
        },
    }
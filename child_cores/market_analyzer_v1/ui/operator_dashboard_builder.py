from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


def _safe_dict(value: Any) -> Optional[Dict[str, Any]]:
    return value if isinstance(value, dict) else None


def _safe_list_of_dicts(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_case_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    panel = _safe_dict(runtime_result.get("case_panel")) or {}
    return {
        "case_id": panel.get("case_id"),
        "title": panel.get("title"),
        "observed_at": panel.get("observed_at"),
        "input_mode": panel.get("input_mode"),
    }


def _extract_runtime_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    panel = _safe_dict(runtime_result.get("runtime_panel")) or {}
    candidates = _safe_list_of_dicts(panel.get("candidates"))
    return {
        "market_regime": panel.get("market_regime"),
        "event_theme": panel.get("event_theme"),
        "macro_bias": panel.get("macro_bias"),
        "headline": panel.get("headline"),
        "candidate_count": _coerce_int(panel.get("candidate_count"), default=len(candidates)),
        "candidates": candidates,
    }


def _extract_recommendation_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    panel = _safe_dict(runtime_result.get("recommendation_panel")) or {}
    items = _safe_list_of_dicts(panel.get("items")) or _safe_list_of_dicts(panel.get("recommendations"))
    return {
        "state": panel.get("state", "present" if items else "empty"),
        "count": _coerce_int(panel.get("count"), default=len(items)),
        "items": items,
    }


def _extract_governance_panel(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    panel = _safe_dict(runtime_result.get("governance_panel")) or {}
    return {
        "mode": runtime_result.get("mode", "advisory"),
        "execution_allowed": bool(runtime_result.get("execution_allowed", False)),
        "approval_required": bool(runtime_result.get("approval_required", True)),
        "watcher_passed": panel.get("watcher_passed"),
        "watcher_status": panel.get("watcher_status"),
        "closeout_status": panel.get("closeout_status"),
        "requires_review": bool(panel.get("requires_review", False)),
        "receipt_id": panel.get("receipt_id"),
        "watcher_validation_id": panel.get("watcher_validation_id"),
        "closeout_id": panel.get("closeout_id"),
    }


def _extract_rejection_panel(runtime_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    panel = _safe_dict(runtime_result.get("rejection_panel"))
    if not panel:
        return None
    return {
        "status": panel.get("status", "rejected"),
        "reason": panel.get("reason"),
        "detail": panel.get("detail"),
        "rejection_class": panel.get("rejection_class"),
    }


def _extract_refinement_panel(runtime_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    panel = _safe_dict(runtime_result.get("refinement_panel"))
    if not panel:
        return None

    return {
        "visible": bool(panel.get("visible", True)),
        "signal": panel.get("signal"),
        "confidence_adjustment": panel.get("confidence_adjustment"),
        "risk_flag": panel.get("risk_flag"),
        "insight": panel.get("insight"),
        "narrative": panel.get("narrative"),
        "source": panel.get("source", "stage16_refinement_arbitrator"),
    }


def _extract_pm_workflow_panel(runtime_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    panel = _safe_dict(runtime_result.get("pm_workflow_panel"))
    if not panel:
        return None

    return {
        "strategy": _safe_dict(panel.get("strategy")) or {},
        "review": _safe_dict(panel.get("review")) or {},
        "plan": _safe_dict(panel.get("plan")) or {},
        "queue": _safe_dict(panel.get("queue")) or {},
        "dispatch": _safe_dict(panel.get("dispatch")) or {},
    }


def _build_external_memory_panel(runtime_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Builds a bounded, advisory-only external memory panel.

    Accepted source shapes:
    1. runtime_result["external_memory_panel"] already present and dict-shaped
    2. runtime_result["external_memory_merge"]["external_memory_panel"]
    3. runtime_result["external_memory_merge"]["panel"]
    4. runtime_result["external_memory_return_packet"]["memory_context_panel"]

    Non-dict values are ignored so the pre-interface watcher will not fail on
    optional-panel shape drift.
    """
    direct_panel = _safe_dict(runtime_result.get("external_memory_panel"))
    if direct_panel:
        panel = deepcopy(direct_panel)
    else:
        merge_payload = _safe_dict(runtime_result.get("external_memory_merge")) or {}
        return_packet = _safe_dict(runtime_result.get("external_memory_return_packet")) or {}

        panel = (
            _safe_dict(merge_payload.get("external_memory_panel"))
            or _safe_dict(merge_payload.get("panel"))
            or _safe_dict(return_packet.get("memory_context_panel"))
            or {}
        )

    if not panel:
        return None

    similar_events = panel.get("similar_events")
    if not isinstance(similar_events, list):
        similar_events = []

    provenance_refs = panel.get("provenance_refs")
    if not isinstance(provenance_refs, list):
        provenance_refs = []

    bounded_panel = {
        "visible": bool(panel.get("visible", True)),
        "source": panel.get("source", "external_memory"),
        "advisory_only": True,
        "pattern_detected": bool(panel.get("pattern_detected", False)),
        "pattern_strength": panel.get("pattern_strength"),
        "historical_confirmation": panel.get("historical_confirmation"),
        "confidence_adjustment": panel.get("confidence_adjustment"),
        "summary": panel.get("summary"),
        "dominant_symbol": panel.get("dominant_symbol"),
        "dominant_sector": panel.get("dominant_sector"),
        "recurrence_count": _coerce_int(panel.get("recurrence_count"), default=0),
        "temporal_span_days": _coerce_int(panel.get("temporal_span_days"), default=0),
        "similar_events": [item for item in similar_events if isinstance(item, dict)],
        "provenance_refs": [item for item in provenance_refs if isinstance(item, (str, int, float))],
    }

    if not bounded_panel["pattern_detected"] and not bounded_panel["summary"] and bounded_panel["recurrence_count"] == 0:
        return None

    return bounded_panel


def build_operator_dashboard(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the canonical operator-facing dashboard payload.

    This function remains advisory-only and never mutates recommendation logic.
    It merely assembles already-governed runtime truth into a stable outward shape.
    """
    if not isinstance(runtime_result, dict):
        raise TypeError("runtime_result must be a dict")

    response: Dict[str, Any] = {
        "status": runtime_result.get("status", "ok"),
        "request_id": runtime_result.get("request_id"),
        "core_id": runtime_result.get("core_id", "market_analyzer_v1"),
        "route_mode": runtime_result.get("route_mode"),
        "mode": runtime_result.get("mode", "advisory"),
        "execution_allowed": bool(runtime_result.get("execution_allowed", False)),
        "case_panel": _extract_case_panel(runtime_result),
        "runtime_panel": _extract_runtime_panel(runtime_result),
        "recommendation_panel": _extract_recommendation_panel(runtime_result),
        "governance_panel": _extract_governance_panel(runtime_result),
    }

    rejection_panel = _extract_rejection_panel(runtime_result)
    if rejection_panel is not None:
        response["rejection_panel"] = rejection_panel

    refinement_panel = _extract_refinement_panel(runtime_result)
    if refinement_panel is not None:
        response["refinement_panel"] = refinement_panel

    pm_workflow_panel = _extract_pm_workflow_panel(runtime_result)
    if pm_workflow_panel is not None:
        response["pm_workflow_panel"] = pm_workflow_panel

    external_memory_panel = _build_external_memory_panel(runtime_result)
    if external_memory_panel is not None:
        response["external_memory_panel"] = external_memory_panel

    return response
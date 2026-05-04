from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


ESCALATION_ROUTING_VERSION = "v1.0"
ARTIFACT_TYPE = "watcher_escalation_route"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _hash(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _extract_watcher_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("watcher_enforcement_decision"))


def _extract_rollback_recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("rollback_recommendation"))


def _severity_from_sources(
    *,
    watcher_decision: Dict[str, Any],
    rollback_recommendation: Dict[str, Any],
) -> str:
    rollback_severity = _clean(rollback_recommendation.get("severity")).lower()

    if rollback_severity in {"critical", "high", "medium", "low"}:
        return rollback_severity

    if watcher_decision.get("blocked") is True:
        return "high"

    if watcher_decision.get("escalation_required") is True:
        return "medium"

    return "low"


def _route_class_from_sources(
    *,
    watcher_decision: Dict[str, Any],
    rollback_recommendation: Dict[str, Any],
) -> str:
    recommendation_class = _clean(
        rollback_recommendation.get("recommendation_class")
    )

    if recommendation_class == "rollback_review_required":
        return "rollback_review"

    if watcher_decision.get("blocked") is True:
        return "blocked_action_review"

    if recommendation_class == "escalation_review_only":
        return "caution_review"

    if watcher_decision.get("escalation_required") is True:
        return "caution_review"

    return "informational"


def _audience_for_route(route_class: str, severity: str) -> List[Dict[str, Any]]:
    if route_class == "rollback_review" or severity in {"critical", "high"}:
        return [
            {
                "audience": "operator",
                "role": "system_operator",
                "required": True,
                "reason": "Operator must review blocked action or rollback recommendation.",
            },
            {
                "audience": "project_manager",
                "role": "pm",
                "required": True,
                "reason": "PM must review affected project artifacts before follow-on work proceeds.",
            },
        ]

    if route_class == "caution_review" or severity == "medium":
        return [
            {
                "audience": "project_manager",
                "role": "pm",
                "required": True,
                "reason": "PM should review caution flags before relying on downstream output.",
            }
        ]

    return [
        {
            "audience": "system_log",
            "role": "audit_log",
            "required": False,
            "reason": "Informational route only.",
        }
    ]


def _channels_for_route(route_class: str, severity: str) -> List[Dict[str, Any]]:
    channels: List[Dict[str, Any]] = [
        {
            "channel": "governance_index",
            "required": True,
            "delivery_allowed": False,
            "reason": "Escalation route should be indexed for awareness and replay.",
        }
    ]

    if route_class in {"rollback_review", "blocked_action_review"}:
        channels.append(
            {
                "channel": "operator_dashboard",
                "required": True,
                "delivery_allowed": False,
                "reason": "Operator dashboard should surface blocking review state.",
            }
        )

    if severity in {"critical", "high", "medium"}:
        channels.append(
            {
                "channel": "project_visibility",
                "required": True,
                "delivery_allowed": False,
                "reason": "Project visibility should show escalation posture.",
            }
        )

    return channels


def _collect_reason_codes(
    *,
    watcher_decision: Dict[str, Any],
    rollback_recommendation: Dict[str, Any],
) -> List[str]:
    codes: List[str] = []

    for item in _safe_list(watcher_decision.get("reasons")):
        code = _clean(_safe_dict(item).get("code"))
        if code:
            codes.append(code)

    for item in _safe_list(watcher_decision.get("escalations")):
        code = _clean(_safe_dict(item).get("code"))
        if code:
            codes.append(code)

    for item in _safe_list(rollback_recommendation.get("reasons")):
        code = _clean(_safe_dict(item).get("code"))
        if code:
            codes.append(code)

    return sorted(set(codes))


def _collect_affected_artifacts(
    rollback_recommendation: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    affected = _safe_dict(rollback_recommendation.get("affected_artifacts"))

    return {
        "artifacts_created": _safe_list(affected.get("artifacts_created")),
        "state_mutations": _safe_list(affected.get("state_mutations")),
        "external_actions": _safe_list(affected.get("external_actions")),
    }


def build_escalation_route(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "watcher_escalation_routing",
) -> Dict[str, Any]:
    """
    Build a sealed escalation route.

    This does not notify anyone.
    This does not mutate state.
    This does not execute rollback.
    """

    source = payload if isinstance(payload, dict) else {}

    watcher_decision = _extract_watcher_decision(source)
    rollback_recommendation = _extract_rollback_recommendation(source)

    severity = _severity_from_sources(
        watcher_decision=watcher_decision,
        rollback_recommendation=rollback_recommendation,
    )
    route_class = _route_class_from_sources(
        watcher_decision=watcher_decision,
        rollback_recommendation=rollback_recommendation,
    )

    reason_codes = _collect_reason_codes(
        watcher_decision=watcher_decision,
        rollback_recommendation=rollback_recommendation,
    )
    affected_artifacts = _collect_affected_artifacts(rollback_recommendation)

    route_seed = {
        "action": action,
        "profile": profile,
        "watcher_decision_hash": watcher_decision.get("decision_hash", ""),
        "rollback_recommendation_hash": rollback_recommendation.get(
            "recommendation_hash",
            "",
        ),
        "severity": severity,
        "route_class": route_class,
    }

    route_id = (
        "watcher_escalation_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "_"
        + _hash(route_seed)[:12]
    )

    route = {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": ESCALATION_ROUTING_VERSION,
        "route_id": route_id,
        "created_at": _utc_now_iso(),
        "profile": _clean(profile),
        "action": _clean(action),
        "actor": _clean(actor) or "watcher_escalation_routing",
        "route_class": route_class,
        "severity": severity,
        "reason_codes": reason_codes,
        "audience": _audience_for_route(route_class, severity),
        "channels": _channels_for_route(route_class, severity),
        "source": {
            "watcher_decision_hash": watcher_decision.get("decision_hash", ""),
            "watcher_status": watcher_decision.get("status", ""),
            "watcher_decision": watcher_decision.get("decision", ""),
            "rollback_recommendation_hash": rollback_recommendation.get(
                "recommendation_hash",
                "",
            ),
            "rollback_recommendation_class": rollback_recommendation.get(
                "recommendation_class",
                "",
            ),
        },
        "affected_artifacts": affected_artifacts,
        "routing_actions": {
            "index_required": True,
            "dashboard_visibility_required": route_class
            in {"rollback_review", "blocked_action_review", "caution_review"},
            "operator_review_required": route_class
            in {"rollback_review", "blocked_action_review"},
            "pm_review_required": route_class
            in {"rollback_review", "blocked_action_review", "caution_review"},
            "external_notification_allowed": False,
            "auto_dispatch_allowed": False,
        },
        "authority": {
            "watcher_owned": True,
            "routing_only": True,
            "may_route": True,
            "may_notify_external": False,
            "may_mutate_state": False,
            "may_execute": False,
            "operator_required": route_class
            in {"rollback_review", "blocked_action_review"},
        },
        "constraints": {
            "no_direct_notification": True,
            "no_direct_state_mutation": True,
            "no_direct_execution": True,
            "no_rollback_execution": True,
            "route_must_be_indexed_before_display": True,
        },
        "sealed": True,
    }

    route["route_hash"] = _hash(
        {
            key: value
            for key, value in route.items()
            if key != "route_hash"
        }
    )

    return route
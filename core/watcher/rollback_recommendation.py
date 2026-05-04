from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


ROLLBACK_RECOMMENDATION_VERSION = "v1.0"
ARTIFACT_TYPE = "watcher_rollback_recommendation"


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


def _extract_result_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("result_summary"))


def _extract_paths_from_result_summary(result_summary: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "artifacts_created": _safe_list(result_summary.get("artifacts_created")),
        "state_mutations": _safe_list(result_summary.get("state_mutations")),
        "external_actions": _safe_list(result_summary.get("external_actions")),
    }


def _extract_watcher_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(payload.get("watcher_enforcement_decision"))


def _derive_recommendation_class(watcher_decision: Dict[str, Any]) -> str:
    if watcher_decision.get("blocked") is True:
        return "rollback_review_required"

    if watcher_decision.get("rollback_recommended") is True:
        return "rollback_review_required"

    if watcher_decision.get("escalation_required") is True:
        return "escalation_review_only"

    return "no_rollback_recommended"


def _derive_severity(watcher_decision: Dict[str, Any]) -> str:
    if watcher_decision.get("blocked") is True:
        return "high"

    if watcher_decision.get("rollback_recommended") is True:
        return "high"

    if watcher_decision.get("escalation_required") is True:
        return "medium"

    return "low"


def _derive_reasons(watcher_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
    reasons = _safe_list(watcher_decision.get("reasons"))
    escalations = _safe_list(watcher_decision.get("escalations"))

    output: List[Dict[str, Any]] = []

    for item in reasons:
        if isinstance(item, dict):
            output.append(
                {
                    "source": "watcher_reason",
                    "code": item.get("code", ""),
                    "severity": item.get("severity", ""),
                    "message": item.get("message", ""),
                    "details": item.get("details", {}),
                }
            )

    for item in escalations:
        if isinstance(item, dict):
            output.append(
                {
                    "source": "watcher_escalation",
                    "code": item.get("code", ""),
                    "severity": item.get("severity", ""),
                    "message": item.get("message", ""),
                    "details": item.get("details", {}),
                }
            )

    return output


def _build_review_steps(
    *,
    recommendation_class: str,
    paths: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if recommendation_class == "no_rollback_recommended":
        return [
            {
                "step": "no_action",
                "description": "No rollback review is recommended.",
                "requires_operator": False,
            }
        ]

    steps: List[Dict[str, Any]] = [
        {
            "step": "freeze_follow_on_actions",
            "description": "Pause follow-on governed actions that depend on the affected artifacts.",
            "requires_operator": True,
        },
        {
            "step": "inspect_result_summary",
            "description": "Review the sealed result summary and watcher enforcement decision.",
            "requires_operator": True,
        },
    ]

    if paths["state_mutations"]:
        steps.append(
            {
                "step": "review_state_mutations",
                "description": "Review state mutation artifacts before deciding whether rollback is needed.",
                "requires_operator": True,
                "targets": paths["state_mutations"],
            }
        )

    if paths["artifacts_created"]:
        steps.append(
            {
                "step": "review_created_artifacts",
                "description": "Review created receipt/artifact records and determine whether they should be superseded, quarantined, or retained.",
                "requires_operator": True,
                "targets": paths["artifacts_created"],
            }
        )

    if paths["external_actions"]:
        steps.append(
            {
                "step": "review_external_actions",
                "description": "External actions cannot be silently rolled back. Review and decide on compensating action.",
                "requires_operator": True,
                "targets": paths["external_actions"],
            }
        )

    steps.append(
        {
            "step": "operator_decision_required",
            "description": "Operator must choose retain, supersede, quarantine, or create compensating action.",
            "requires_operator": True,
        }
    )

    return steps


def build_rollback_recommendation(
    *,
    payload: Dict[str, Any],
    action: str,
    profile: str,
    actor: str = "watcher_rollback_recommendation",
) -> Dict[str, Any]:
    """
    Build a sealed rollback recommendation.

    This never mutates state.
    This never deletes artifacts.
    This never executes rollback.
    """

    source = payload if isinstance(payload, dict) else {}

    result_summary = _extract_result_summary(source)
    watcher_decision = _extract_watcher_decision(source)

    paths = _extract_paths_from_result_summary(result_summary)
    recommendation_class = _derive_recommendation_class(watcher_decision)
    severity = _derive_severity(watcher_decision)
    reasons = _derive_reasons(watcher_decision)

    recommendation = {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_version": ROLLBACK_RECOMMENDATION_VERSION,
        "created_at": _utc_now_iso(),
        "profile": _clean(profile),
        "action": _clean(action),
        "actor": _clean(actor) or "watcher_rollback_recommendation",
        "recommendation_class": recommendation_class,
        "severity": severity,
        "rollback_execution_allowed": False,
        "state_mutation_allowed": False,
        "external_action_allowed": False,
        "source": {
            "watcher_decision_hash": watcher_decision.get("decision_hash", ""),
            "watcher_status": watcher_decision.get("status", ""),
            "watcher_decision": watcher_decision.get("decision", ""),
            "result_summary_hash": _hash(result_summary) if result_summary else "",
            "result_effect": result_summary.get("effect", ""),
            "result_status": result_summary.get("status", ""),
        },
        "affected_artifacts": paths,
        "reasons": reasons,
        "recommended_steps": _build_review_steps(
            recommendation_class=recommendation_class,
            paths=paths,
        ),
        "authority": {
            "watcher_owned": True,
            "recommendation_only": True,
            "may_recommend_rollback": True,
            "may_execute_rollback": False,
            "may_mutate_state": False,
            "operator_required": recommendation_class != "no_rollback_recommended",
        },
        "constraints": {
            "no_direct_execution": True,
            "no_direct_state_mutation": True,
            "no_artifact_deletion": True,
            "no_silent_reversal": True,
            "compensating_action_requires_governance": True,
        },
        "sealed": True,
    }

    recommendation["recommendation_hash"] = _hash(
        {
            key: value
            for key, value in recommendation.items()
            if key != "recommendation_hash"
        }
    )

    return recommendation
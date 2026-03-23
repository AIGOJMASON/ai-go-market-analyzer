from __future__ import annotations

from typing import Any, Dict


def evaluate_pm_propagation(
    *,
    interpretation: Dict[str, Any],
) -> Dict[str, Any]:
    trust_class = interpretation.get("trust_class")
    screening_status = interpretation.get("screening_status")
    recommended_action = interpretation.get("recommended_action")
    priority = interpretation.get("priority")

    reasons = []

    if screening_status != "passed":
        reasons.append("screening_not_passed")

    if trust_class != "verified":
        reasons.append(f"trust_class_not_propagation_ready:{trust_class}")

    if recommended_action != "prepare_inheritance":
        reasons.append(f"recommended_action_not_propagation_ready:{recommended_action}")

    if priority not in {"high", "medium"}:
        reasons.append(f"priority_not_propagation_ready:{priority}")

    if reasons:
        decision = "retain_in_pm"
    else:
        decision = "propagate_to_inheritance"

    return {
        "decision_type": "pm_propagation_decision",
        "decision": decision,
        "trust_class": trust_class,
        "screening_status": screening_status,
        "recommended_action": recommended_action,
        "priority": priority,
        "reasons": reasons,
    }